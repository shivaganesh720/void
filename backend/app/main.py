import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.contracts.enums import ApprovalStatus, MissionStatus, TaskStatus
from app.contracts.schemas import ApprovalDecisionUpdate, ApprovalRequest, ApprovalResponse, DashboardSummaryResponse, HealthResponse, MissionDetailResponse, MissionEventResponse, MissionListResponse, ResumeJdMissionCreate, TaskResponse
from app.control_plane.state import validate_transition
from app.core.config import get_settings
from app.db.runtime import RuntimeStore
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
class StoredApproval:
    id: UUID
    mission_id: UUID
    task_id: UUID | None
    requested_action: str
    risk_reason: str
    required_by_policy: bool = False
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    reviewed_at: datetime | None = None
    reviewer_id: str | None = None
    reviewer_comment: str | None = None
    expiration: datetime | None = None
    metadata: dict = field(default_factory=dict)


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
    approval_required: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    events: list[MissionEventResponse] = field(default_factory=list)
    approvals: list[StoredApproval] = field(default_factory=list)


def _approval_payload(approval: StoredApproval) -> dict:
    return {
        "id": approval.id,
        "mission_id": approval.mission_id,
        "task_id": approval.task_id,
        "requested_action": approval.requested_action,
        "risk_reason": approval.risk_reason,
        "required_by_policy": approval.required_by_policy,
        "status": approval.status.value,
        "requested_at": approval.requested_at,
        "reviewed_at": approval.reviewed_at,
        "reviewer_id": approval.reviewer_id,
        "reviewer_comment": approval.reviewer_comment,
        "expiration": approval.expiration,
        "metadata": approval.metadata,
    }


def _approval_from_payload(payload: dict) -> StoredApproval:
    return StoredApproval(
        id=UUID(payload["id"]),
        mission_id=UUID(payload["mission_id"]),
        task_id=UUID(payload["task_id"]) if payload.get("task_id") else None,
        requested_action=payload["requested_action"],
        risk_reason=payload["risk_reason"],
        required_by_policy=payload.get("required_by_policy", False),
        status=ApprovalStatus(payload["status"]),
        requested_at=datetime.fromisoformat(payload["requested_at"]),
        reviewed_at=datetime.fromisoformat(payload["reviewed_at"]) if payload.get("reviewed_at") else None,
        reviewer_id=payload.get("reviewer_id"),
        reviewer_comment=payload.get("reviewer_comment"),
        expiration=datetime.fromisoformat(payload["expiration"]) if payload.get("expiration") else None,
        metadata=payload.get("metadata", {}),
    )


def _mission_payload(mission: StoredMission) -> dict:
    return {
        "id": mission.id,
        "project_id": mission.project_id,
        "intent": mission.intent,
        "status": mission.status.value,
        "task": {
            "id": mission.task.id,
            "mission_id": mission.task.mission_id,
            "name": mission.task.name,
            "status": mission.task.status.value,
            "result": mission.task.result,
            "error": mission.task.error,
        },
        "result": mission.result,
        "error": mission.error,
        "execution_mode": mission.execution_mode,
        "approval_required": mission.approval_required,
        "created_at": mission.created_at,
        "updated_at": mission.updated_at,
        "completed_at": mission.completed_at,
        "events": [event.model_dump(mode="json") for event in mission.events],
        "approvals": [_approval_payload(approval) for approval in mission.approvals],
    }


def _mission_from_payload(payload: dict) -> StoredMission:
    task_payload = payload["task"]
    task = StoredTask(
        id=UUID(task_payload["id"]),
        mission_id=UUID(task_payload["mission_id"]),
        name=task_payload["name"],
        status=TaskStatus(task_payload["status"]),
        result=task_payload.get("result"),
        error=task_payload.get("error"),
    )
    return StoredMission(
        id=UUID(payload["id"]),
        project_id=UUID(payload["project_id"]),
        intent=payload["intent"],
        status=MissionStatus(payload["status"]),
        task=task,
        result=payload.get("result"),
        error=payload.get("error"),
        execution_mode=payload.get("execution_mode", "AUTO"),
        approval_required=payload.get("approval_required", False),
        created_at=datetime.fromisoformat(payload["created_at"]),
        updated_at=datetime.fromisoformat(payload["updated_at"]),
        completed_at=datetime.fromisoformat(payload["completed_at"]) if payload.get("completed_at") else None,
        events=[MissionEventResponse.model_validate(event) for event in payload.get("events", [])],
        approvals=[_approval_from_payload(approval) for approval in payload.get("approvals", [])],
    )


RUNTIME_STORE = RuntimeStore(settings.runtime_db_path)
MISSIONS: dict[UUID, StoredMission] = {
    mission.id: mission for mission in (_mission_from_payload(payload) for payload in RUNTIME_STORE.load_all())
}


def _persist_mission(mission: StoredMission) -> None:
    RUNTIME_STORE.save(_mission_payload(mission))


def _record_event(mission: StoredMission, event_type: str, detail: str) -> None:
    timestamp = datetime.now(UTC)
    mission.updated_at = timestamp
    mission.events.append(MissionEventResponse(id=uuid4(), mission_id=mission.id, event_type=event_type, timestamp=timestamp, detail=detail))
    _persist_mission(mission)


def _task_response(task: StoredTask) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        mission_id=task.mission_id,
        name=task.name,
        status=task.status.value,
        result=task.result,
        error=task.error,
    )


def _approval_response(approval: StoredApproval) -> ApprovalResponse:
    return ApprovalResponse(
        id=approval.id,
        mission_id=approval.mission_id,
        task_id=approval.task_id,
        requested_action=approval.requested_action,
        risk_reason=approval.risk_reason,
        required_by_policy=approval.required_by_policy,
        status=approval.status,
        requested_at=approval.requested_at,
        reviewed_at=approval.reviewed_at,
        reviewer_id=approval.reviewer_id,
        reviewer_comment=approval.reviewer_comment,
        expiration=approval.expiration,
        metadata=approval.metadata,
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
        approval_required=mission.approval_required,
        events=mission.events,
        approvals=[_approval_response(approval) for approval in mission.approvals],
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
        _persist_mission(mission)
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


@app.post("/api/v1/missions/{mission_id}/approvals", response_model=ApprovalResponse, status_code=201, tags=["missions"])
def request_mission_approval(
    mission_id: UUID,
    project_id: UUID = Query(...),
    request: ApprovalRequest = None,
) -> ApprovalResponse:
    if request is None:
        raise HTTPException(status_code=422, detail="Approval request body is required")

    mission = MISSIONS.get(mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    approval = StoredApproval(
        id=uuid4(),
        mission_id=mission.id,
        task_id=mission.task.id,
        requested_action=request.requested_action,
        risk_reason=request.risk_reason,
        required_by_policy=request.required_by_policy,
        reviewer_id=request.reviewer_id,
        expiration=datetime.now(UTC) if request.required_by_policy else None,
    )
    mission.approvals.append(approval)
    mission.approval_required = True

    if mission.status not in {MissionStatus.CANCELLED, MissionStatus.FAILED, MissionStatus.COMPLETED}:
        try:
            validate_transition(mission.status, MissionStatus.WAITING_FOR_APPROVAL)
            mission.status = MissionStatus.WAITING_FOR_APPROVAL
        except ValueError:
            mission.status = MissionStatus.WAITING_FOR_APPROVAL

    _record_event(mission, "APPROVAL_REQUESTED", f"Approval requested: {request.requested_action}")
    _persist_mission(mission)
    return _approval_response(approval)


@app.patch("/api/v1/missions/{mission_id}/approvals/{approval_id}", response_model=ApprovalResponse, tags=["missions"])
def review_mission_approval(
    mission_id: UUID,
    approval_id: UUID,
    project_id: UUID = Query(...),
    request: ApprovalDecisionUpdate = None,
) -> ApprovalResponse:
    if request is None:
        raise HTTPException(status_code=422, detail="Approval decision body is required")

    mission = MISSIONS.get(mission_id)
    if mission is None or mission.project_id != project_id:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    approval = next((item for item in mission.approvals if item.id == approval_id), None)
    if approval is None:
        raise HTTPException(status_code=404, detail="APPROVAL_NOT_FOUND")

    approval.status = request.decision
    approval.reviewed_at = datetime.now(UTC)
    approval.reviewer_id = request.reviewer_id or approval.reviewer_id
    approval.reviewer_comment = request.reviewer_comment

    if request.decision == ApprovalStatus.APPROVED:
        if mission.status == MissionStatus.WAITING_FOR_APPROVAL:
            try:
                validate_transition(mission.status, MissionStatus.APPROVED)
                mission.status = MissionStatus.APPROVED
            except ValueError:
                mission.status = MissionStatus.APPROVED
        mission.approval_required = False
    elif request.decision == ApprovalStatus.REJECTED:
        mission.approval_required = False
        try:
            validate_transition(mission.status, MissionStatus.BLOCKED)
            mission.status = MissionStatus.BLOCKED
        except ValueError:
            mission.status = MissionStatus.BLOCKED
    elif request.decision == ApprovalStatus.CANCELLED:
        mission.approval_required = False
        try:
            validate_transition(mission.status, MissionStatus.CANCELLED)
            mission.status = MissionStatus.CANCELLED
        except ValueError:
            mission.status = MissionStatus.CANCELLED

    _record_event(mission, "APPROVAL_DECISION", f"Approval {request.decision.value} for {approval.requested_action}")
    _persist_mission(mission)
    return _approval_response(approval)