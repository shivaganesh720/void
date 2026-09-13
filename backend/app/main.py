import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.contracts.enums import MissionStatus, TaskStatus
from app.contracts.schemas import DashboardSummaryResponse, HealthResponse, MissionDetailResponse, MissionEventResponse, MissionListResponse, ResumeJdMissionCreate, TaskResponse
from app.control_plane.state import validate_transition
from app.core.config import get_settings
from app.files.parsing import ParsedDocument, parse_document
from app.workflows.resume_jd import analyze_resume_against_jd
from app.workflows.resume_jd_analysis import build_analysis, validate_analysis


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
logger = logging.getLogger("void.execution")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "PATCH"],
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
    execution_mode: str = "AUTO"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    events: list[MissionEventResponse] = field(default_factory=list)


def _record_event(mission: StoredMission, event_type: str, detail: str) -> None:
    timestamp = datetime.now(UTC)
    mission.updated_at = timestamp
    mission.events.append(MissionEventResponse(id=uuid4(), mission_id=mission.id, event_type=event_type, timestamp=timestamp, detail=detail))


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
        created_at=mission.created_at,
        updated_at=mission.updated_at,
        completed_at=mission.completed_at,
        execution_mode=mission.execution_mode,
        events=mission.events,
    )


def _mission_list_response(mission: StoredMission) -> MissionListResponse:
    return MissionListResponse(
        id=mission.id,
        project_id=mission.project_id,
        intent=mission.intent,
        status=mission.status,
        task=_task_response(mission.task),
        created_at=mission.created_at,
    )


def _execute_resume_jd(mission: StoredMission, resume_text: str, job_description: str) -> None:
    """Run the bounded local workflow and persist every terminal state in the store."""
    validate_transition(mission.status, MissionStatus.VALIDATING)
    mission.status = MissionStatus.VALIDATING
    _record_event(mission, "VALIDATION_STARTED", "Resume and job description inputs accepted.")
    validate_transition(mission.status, MissionStatus.PLANNED)
    mission.status = MissionStatus.PLANNED
    validate_transition(mission.status, MissionStatus.APPROVED)
    mission.status = MissionStatus.APPROVED
    validate_transition(mission.status, MissionStatus.RUNNING)
    mission.status = MissionStatus.RUNNING
    _record_event(mission, "MISSION_STARTED", "Bounded Resume/JD workflow started.")
    validate_transition(mission.task.status, TaskStatus.READY)
    mission.task.status = TaskStatus.READY
    validate_transition(mission.task.status, TaskStatus.QUEUED)
    mission.task.status = TaskStatus.QUEUED
    validate_transition(mission.task.status, TaskStatus.RUNNING)
    mission.task.status = TaskStatus.RUNNING
    logger.info("execution_started mission_id=%s task_id=%s", mission.id, mission.task.id)
    try:
        resume = ParsedDocument("RESUME", "pasted-resume.txt", resume_text, len(resume_text), "SUCCEEDED")
        jd = ParsedDocument("JOB_DESCRIPTION", "pasted-job-description.txt", job_description, len(job_description), "SUCCEEDED")
        structured = build_analysis(resume, jd, str(mission.id))
        validate_analysis(structured)
        analysis = analyze_resume_against_jd(resume_text, job_description)
        mission.result = {
            **structured,
            "required_skills": list(analysis.required_skills),
            "resume_skills": list(analysis.resume_skills),
            "matching_skills": list(analysis.matching_skills),
            "missing_skills": list(analysis.missing_skills),
            "overall_match_explanation": structured["match_analysis"]["score_explanation"],
            "recommendations": list(analysis.recommendations),
        }
        mission.task.result = mission.result
        validate_transition(mission.task.status, TaskStatus.SUCCEEDED)
        mission.task.status = TaskStatus.SUCCEEDED
        validate_transition(mission.status, MissionStatus.COMPLETED)
        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.now(UTC)
        _record_event(mission, "MISSION_COMPLETED", "Analysis validated and persisted in the development store.")
        logger.info("execution_succeeded mission_id=%s task_id=%s", mission.id, mission.task.id)
    except Exception as exc:
        mission.task.error = "WORKFLOW_FAILED"
        mission.error = "Resume/JD analysis failed."
        validate_transition(mission.task.status, TaskStatus.FAILED)
        mission.task.status = TaskStatus.FAILED
        validate_transition(mission.status, MissionStatus.FAILED)
        mission.status = MissionStatus.FAILED
        _record_event(mission, "MISSION_FAILED", mission.error)
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
    _record_event(mission, "MISSION_CREATED", "Resume/JD mission created.")
    logger.info("mission_received mission_id=%s task_id=%s", mission_id, task.id)
    _execute_resume_jd(mission, request.resume_text, request.job_description)
    return _mission_response(mission)


@app.post("/api/v1/missions/resume-jd/upload", response_model=MissionDetailResponse, status_code=201, tags=["missions"])
async def create_resume_jd_upload_mission(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
    project_id: UUID = Form(default=UUID("00000000-0000-0000-0000-000000000001")),
) -> MissionDetailResponse:
    """Ingest both documents through the file validator before mission execution."""
    try:
        resume_document = parse_document(resume.filename or "resume.txt", resume.content_type or "application/octet-stream", await resume.read(), "RESUME", settings.max_upload_bytes)
        jd_document = parse_document(job_description.filename or "jd.txt", job_description.content_type or "application/octet-stream", await job_description.read(), "JOB_DESCRIPTION", settings.max_upload_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    mission_id = uuid4()
    task = StoredTask(id=uuid4(), mission_id=mission_id, name="resume_jd_analysis")
    mission = StoredMission(id=mission_id, project_id=project_id, intent="Compare uploaded resume with job description", status=MissionStatus.DRAFT, task=task)
    MISSIONS[mission_id] = mission
    _record_event(mission, "MISSION_CREATED", "Uploaded Resume/JD mission created.")
    _execute_resume_jd(mission, resume_document.extracted_text, jd_document.extracted_text)
    if mission.result:
        mission.result["resume"]["file_name"] = resume_document.file_name
        mission.result["job_description"]["file_name"] = jd_document.file_name
        mission.result["warnings"] = list(set(mission.result["warnings"]) | set(resume_document.warnings) | set(jd_document.warnings))
    return _mission_response(mission)


@app.get("/api/v1/missions", response_model=list[MissionListResponse], tags=["missions"])
def list_missions(
    project_id: UUID = Query(...),
    status: MissionStatus | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[MissionListResponse]:
    missions = [mission for mission in MISSIONS.values() if mission.project_id == project_id]
    if status is not None:
        missions = [mission for mission in missions if mission.status == status]
    if search:
        normalized_search = search.casefold()
        missions = [mission for mission in missions if normalized_search in mission.intent.casefold() or normalized_search in str(mission.id).casefold()]
    ordered = sorted(missions, key=lambda item: item.updated_at, reverse=True)
    return [_mission_list_response(mission) for mission in ordered[offset:offset + limit]]


@app.get("/api/v1/dashboard/summary", response_model=DashboardSummaryResponse, tags=["dashboard"])
def dashboard_summary(project_id: UUID = Query(...)) -> DashboardSummaryResponse:
    missions = [mission for mission in MISSIONS.values() if mission.project_id == project_id]
    return DashboardSummaryResponse(
        project_id=project_id,
        total_missions=len(missions),
        running_missions=sum(mission.status == MissionStatus.RUNNING for mission in missions),
        completed_missions=sum(mission.status == MissionStatus.COMPLETED for mission in missions),
        failed_missions=sum(mission.status == MissionStatus.FAILED for mission in missions),
        blocked_missions=sum(mission.status == MissionStatus.BLOCKED for mission in missions),
        recent_missions=[_mission_list_response(mission) for mission in sorted(missions, key=lambda item: item.created_at, reverse=True)[:5]],
    )


@app.get("/api/v1/missions/{mission_id}", response_model=MissionDetailResponse, tags=["missions"])
def get_mission(mission_id: UUID, project_id: UUID = Query(...)) -> MissionDetailResponse:
    mission = MISSIONS.get(mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")
    return _mission_response(mission)


@app.get("/api/v1/missions/{mission_id}/tasks", response_model=list[TaskResponse], tags=["missions"])
def get_mission_tasks(mission_id: UUID, project_id: UUID = Query(...)) -> list[TaskResponse]:
    mission = MISSIONS.get(mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")
    return [_task_response(mission.task)]


@app.get("/api/v1/missions/{mission_id}/events", response_model=list[MissionEventResponse], tags=["missions"])
def get_mission_events(mission_id: UUID, project_id: UUID = Query(...)) -> list[MissionEventResponse]:
    mission = MISSIONS.get(mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")
    return mission.events