import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.contracts.enums import MissionStatus, TaskStatus
from app.contracts.schemas import HealthResponse, MissionDetailResponse, ResumeJdMissionCreate, TaskResponse
from app.control_plane.state import validate_transition
from app.core.config import get_settings
from app.workflows.resume_jd import analyze_resume_against_jd


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
logger = logging.getLogger("void.execution")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@dataclass
class StoredTask:
    id: UUID
    mission_id: UUID
    name: str
    status: TaskStatus = TaskStatus.CREATED
    result: dict | None = None
    error: str | None = None


@dataclass
class StoredMission:
    id: UUID
    project_id: UUID
    intent: str
    status: MissionStatus
    task: StoredTask
    result: dict | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# This is deliberately an explicit development store until SQLAlchemy sessions and migrations exist.
MISSIONS: dict[UUID, StoredMission] = {}


def _task_response(task: StoredTask) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        mission_id=task.mission_id,
        name=task.name,
        status=task.status.value,
        result=task.result,
        error=task.error,
    )


def _mission_response(mission: StoredMission) -> MissionDetailResponse:
    return MissionDetailResponse(
        id=mission.id,
        project_id=mission.project_id,
        intent=mission.intent,
        status=mission.status,
        task=_task_response(mission.task),
        result=mission.result,
        error=mission.error,
    )


def _execute_resume_jd(mission: StoredMission, resume_text: str, job_description: str) -> None:
    """Run the bounded local workflow and persist every terminal state in the store."""
    validate_transition(mission.status, MissionStatus.VALIDATING)
    mission.status = MissionStatus.VALIDATING
    validate_transition(mission.status, MissionStatus.PLANNED)
    mission.status = MissionStatus.PLANNED
    validate_transition(mission.status, MissionStatus.APPROVED)
    mission.status = MissionStatus.APPROVED
    validate_transition(mission.status, MissionStatus.RUNNING)
    mission.status = MissionStatus.RUNNING
    validate_transition(mission.task.status, TaskStatus.READY)
    mission.task.status = TaskStatus.READY
    validate_transition(mission.task.status, TaskStatus.QUEUED)
    mission.task.status = TaskStatus.QUEUED
    validate_transition(mission.task.status, TaskStatus.RUNNING)
    mission.task.status = TaskStatus.RUNNING
    logger.info("execution_started mission_id=%s task_id=%s", mission.id, mission.task.id)
    try:
        analysis = analyze_resume_against_jd(resume_text, job_description)
        mission.result = {
            "required_skills": list(analysis.required_skills),
            "resume_skills": list(analysis.resume_skills),
            "matching_skills": list(analysis.matching_skills),
            "missing_skills": list(analysis.missing_skills),
            "experience_alignment": "Not evaluated by the bounded lexical workflow.",
            "education_alignment": "Not evaluated by the bounded lexical workflow.",
            "overall_match_explanation": (
                f"Matched {len(analysis.matching_skills)} of "
                f"{len(analysis.required_skills)} normalized job-description terms."
            ),
            "evidence": [
                {"source": item.source, "quote": item.quote, "label": item.label}
                for item in analysis.evidence
            ],
            "warnings": [
                "This V1 workflow performs lexical comparison only; no model provider was called.",
                "Experience and education alignment require structured document extraction.",
            ],
            "recommendations": list(analysis.recommendations),
        }
        mission.task.result = mission.result
        validate_transition(mission.task.status, TaskStatus.SUCCEEDED)
        mission.task.status = TaskStatus.SUCCEEDED
        validate_transition(mission.status, MissionStatus.COMPLETED)
        mission.status = MissionStatus.COMPLETED
        logger.info("execution_succeeded mission_id=%s task_id=%s", mission.id, mission.task.id)
    except Exception as exc:
        mission.task.error = "WORKFLOW_FAILED"
        mission.error = "Resume/JD analysis failed."
        validate_transition(mission.task.status, TaskStatus.FAILED)
        mission.task.status = TaskStatus.FAILED
        validate_transition(mission.status, MissionStatus.FAILED)
        mission.status = MissionStatus.FAILED
        logger.exception("execution_failed mission_id=%s task_id=%s", mission.id, mission.task.id)
        raise exc


@app.get("/health/live", response_model=HealthResponse, tags=["health"])
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
def readiness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)


@app.post("/api/v1/missions/resume-jd", response_model=MissionDetailResponse, status_code=201, tags=["missions"])
def create_resume_jd_mission(request: ResumeJdMissionCreate) -> MissionDetailResponse:
    mission_id = uuid4()
    task = StoredTask(id=uuid4(), mission_id=mission_id, name="resume_jd_analysis")
    mission = StoredMission(
        id=mission_id,
        project_id=request.project_id,
        intent="Compare resume with job description",
        status=MissionStatus.DRAFT,
        task=task,
    )
    MISSIONS[mission_id] = mission
    logger.info("mission_received mission_id=%s task_id=%s", mission_id, task.id)
    _execute_resume_jd(mission, request.resume_text, request.job_description)
    return _mission_response(mission)


@app.get("/api/v1/missions/{mission_id}", response_model=MissionDetailResponse, tags=["missions"])
def get_mission(mission_id: UUID) -> MissionDetailResponse:
    mission = MISSIONS.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")
    return _mission_response(mission)