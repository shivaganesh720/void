import logging
from datetime import UTC, datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db, get_current_user, require_project_access
from app.models.enums import MissionStatus, TaskStatus
from app.schemas import (
    ResumeJdMissionCreate,
    UniversalMissionCreate,
    MissionDetailResponse,
    MissionListResponse,
    DashboardSummaryResponse,
    MissionEventResponse
)
from app.core.config import get_settings
from app.models.base import User, Project, Mission, Task, LifecycleEvent, ProjectMember, Approval, ExecutionProfile, Artifact, Evidence, CostRecord
from app.utils.text import ParsedDocument, parse_document
from app.repositories.projects import project_repo
from app.capabilities.resume_jd.service import analyze_resume_against_jd
from app.capabilities.resume_jd.parser import build_analysis, validate_analysis
from app.execution.task_state import validate_transition
from app.api.deps import DEFAULT_DEMO_USER_ID
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.broker import AgentRegistry, AgentHarness
from app.execution.orchestrator import MissionOrchestrator

router = APIRouter(tags=["missions"])
logger = logging.getLogger("void.execution")
settings = get_settings()


def _ensure_project_access(db: DbSession, project_id: UUID, user: User) -> Project:
    """Validate project access, auto-provisioning for the demo user."""
    project = project_repo.get(db, project_id)
    if not project:
        if user.id == DEFAULT_DEMO_USER_ID:
            project = project_repo.create(db, {
                "id": project_id,
                "name": "Legacy Local Project",
                "owner_id": user.id,
            })
            member = ProjectMember(project_id=project.id, user_id=user.id, role="OWNER")
            db.add(member)
            db.flush()
            return project
        raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")
    # Demo user always has full access regardless of ownership
    if user.id == DEFAULT_DEMO_USER_ID:
        return project
    if project.owner_id != user.id and not project_repo.has_access(db, project_id, user.id):
        raise HTTPException(status_code=403, detail="PROJECT_ACCESS_DENIED")
    return project


def _record_event(db: DbSession, mission: Mission, event_type: str, detail: str) -> None:
    timestamp = datetime.now(UTC)
    mission.updated_at = timestamp
    event = LifecycleEvent(
        mission_id=mission.id,
        event_type=event_type,
        detail=detail
    )
    db.add(event)
    db.flush()


def _execute_resume_jd(db: DbSession, mission: Mission, task: Task, resume_text: str, job_description: str) -> None:
    validate_transition(MissionStatus(mission.status), MissionStatus.VALIDATING)
    mission.status = MissionStatus.VALIDATING.value
    _record_event(db, mission, "VALIDATION_STARTED", "Resume and job description inputs accepted.")

    validate_transition(MissionStatus(mission.status), MissionStatus.PLANNED)
    mission.status = MissionStatus.PLANNED.value
    validate_transition(MissionStatus(mission.status), MissionStatus.APPROVED)
    mission.status = MissionStatus.APPROVED.value
    validate_transition(MissionStatus(mission.status), MissionStatus.RUNNING)
    mission.status = MissionStatus.RUNNING.value
    _record_event(db, mission, "MISSION_STARTED", "Bounded Resume/JD workflow started.")

    validate_transition(TaskStatus(task.status), TaskStatus.READY)
    task.status = TaskStatus.READY.value
    validate_transition(TaskStatus(task.status), TaskStatus.QUEUED)
    task.status = TaskStatus.QUEUED.value
    validate_transition(TaskStatus(task.status), TaskStatus.RUNNING)
    task.status = TaskStatus.RUNNING.value

    try:
        resume = ParsedDocument("RESUME", "pasted-resume.txt", resume_text, len(resume_text), "SUCCEEDED")
        jd = ParsedDocument("JOB_DESCRIPTION", "pasted-job-description.txt", job_description, len(job_description), "SUCCEEDED")
        structured = build_analysis(resume, jd, str(mission.id))
        validate_analysis(structured)
        analysis = analyze_resume_against_jd(resume_text, job_description)

        result_payload = {
            **structured,
            "required_skills": list(analysis.required_skills),
            "resume_skills": list(analysis.resume_skills),
            "matching_skills": list(analysis.matching_skills),
            "missing_skills": list(analysis.missing_skills),
            "overall_match_explanation": structured["match_analysis"]["score_explanation"],
            "recommendations": list(analysis.recommendations),
        }

        mission.metadata_json = {"result": result_payload}
        task.result_json = result_payload

        validate_transition(TaskStatus(task.status), TaskStatus.SUCCEEDED)
        task.status = TaskStatus.SUCCEEDED.value
        validate_transition(MissionStatus(mission.status), MissionStatus.COMPLETED)
        mission.status = MissionStatus.COMPLETED.value
        mission.completed_at = datetime.now(UTC)
        _record_event(db, mission, "MISSION_COMPLETED", "Analysis validated and persisted.")
    except Exception as exc:
        task.error = "WORKFLOW_FAILED"
        mission.error = "Resume/JD analysis failed."
        validate_transition(TaskStatus(task.status), TaskStatus.FAILED)
        task.status = TaskStatus.FAILED.value
        validate_transition(MissionStatus(mission.status), MissionStatus.FAILED)
        mission.status = MissionStatus.FAILED.value
        _record_event(db, mission, "MISSION_FAILED", mission.error)
        logger.exception("execution_failed mission_id=%s task_id=%s", mission.id, task.id)
        raise exc


def _format_mission(mission: Mission, task: Task, events: list[LifecycleEvent], db: DbSession | None = None) -> dict:
    formatted_events = [
        MissionEventResponse(
            id=e.id,
            mission_id=e.mission_id,
            event_type=e.event_type,
            timestamp=e.updated_at,
            detail=e.detail
        ) for e in events
    ]
    approvals = []
    profile = None
    if db is not None:
        profile_record = db.query(ExecutionProfile).filter(ExecutionProfile.mission_id == mission.id).first()
        profile = profile_record.profile_json if profile_record else None
        approvals = [
            {
                "id": approval.id,
                "mission_id": approval.mission_id,
                "task_id": approval.task_id,
                "requested_action": approval.requested_action,
                "risk_reason": approval.risk_reason,
                "required_by_policy": approval.required_by_policy,
                "status": approval.status,
                "requested_at": approval.created_at,
                "reviewed_at": approval.reviewed_at,
                "reviewer_id": approval.reviewer_id,
                "reviewer_comment": approval.reviewer_comment,
                "expiration": approval.expiration,
                "metadata": approval.metadata_json or {},
            }
            for approval in db.query(Approval).filter(Approval.mission_id == mission.id).order_by(Approval.created_at.desc()).all()
        ]
    return {
        "id": mission.id,
        "project_id": mission.project_id,
        "intent": mission.intent,
        "status": mission.status,
        "task": {
            "id": task.id,
            "mission_id": task.mission_id,
            "name": task.name,
            "status": task.status,
            "result": task.result_json,
            "error": task.error
        },
        "result": mission.metadata_json.get("result") if mission.metadata_json else None,
        "error": mission.error,
        "execution_mode": mission.execution_mode,
        "execution_profile": profile,
        "approval_required": mission.approval_required,
        "created_at": mission.created_at,
        "updated_at": mission.updated_at,
        "completed_at": mission.completed_at,
        "events": formatted_events,
        "approvals": approvals,
    }


@router.post("/api/v1/missions/resume-jd", response_model=MissionDetailResponse, status_code=201)
def create_resume_jd_mission(
    request: ResumeJdMissionCreate,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    project = _ensure_project_access(db, request.project_id, current_user)

    mission = Mission(
        project_id=project.id,
        intent="Compare resume with job description",
        status=MissionStatus.DRAFT.value,
        execution_mode=request.execution_profile.execution_mode if request.execution_profile else "AUTO",
    )
    db.add(mission)
    db.flush()

    task = Task(mission_id=mission.id, name="resume_jd_analysis")
    db.add(task)
    db.flush()

    _record_event(db, mission, "MISSION_CREATED", "Resume/JD mission created.")
    _execute_resume_jd(db, mission, task, request.resume_text, request.job_description)
    db.commit()

    db.refresh(mission)
    db.refresh(task)
    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).all()

    return _format_mission(mission, task, events)


@router.post("/api/v1/missions/universal", response_model=MissionDetailResponse, status_code=201)
def create_universal_mission(
    request: UniversalMissionCreate,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    project = _ensure_project_access(db, request.project_id, current_user)
    orchestrator = MissionOrchestrator()
    mission, task = orchestrator.create_and_plan(
        db,
        project_id=project.id,
        user=current_user,
        prompt=request.prompt,
        execution_profile=request.execution_profile,
    )
    if mission.status == MissionStatus.READY.value:
        orchestrator.execute(db, mission=mission, task=task, user=current_user)
    db.commit()
    db.refresh(mission)
    db.refresh(task)
    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).order_by(LifecycleEvent.created_at).all()
    return _format_mission(mission, task, events, db)


@router.post("/api/v1/missions/resume-jd/upload", response_model=MissionDetailResponse, status_code=201)
async def create_resume_jd_upload_mission(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
    project_id: UUID = Form(default=UUID("00000000-0000-0000-0000-000000000001")),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    project = _ensure_project_access(db, project_id, current_user)

    try:
        resume_document = parse_document(resume.filename or "resume.txt", resume.content_type or "application/octet-stream", await resume.read(), "RESUME", settings.max_upload_bytes)
        jd_document = parse_document(job_description.filename or "jd.txt", job_description.content_type or "application/octet-stream", await job_description.read(), "JOB_DESCRIPTION", settings.max_upload_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    mission = Mission(
        project_id=project.id,
        intent="Compare uploaded resume with job description",
        status=MissionStatus.DRAFT.value,
        execution_mode="AUTO"
    )
    db.add(mission)
    db.flush()

    task = Task(mission_id=mission.id, name="resume_jd_analysis")
    db.add(task)
    db.flush()

    _record_event(db, mission, "MISSION_CREATED", "Uploaded Resume/JD mission created.")
    _execute_resume_jd(db, mission, task, resume_document.extracted_text, jd_document.extracted_text)

    if mission.metadata_json and "result" in mission.metadata_json:
        mission.metadata_json["result"]["resume"]["file_name"] = resume_document.file_name
        mission.metadata_json["result"]["job_description"]["file_name"] = jd_document.file_name

    db.commit()

    db.refresh(mission)
    db.refresh(task)
    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).all()

    return _format_mission(mission, task, events)


@router.get("/api/v1/missions", response_model=list[MissionListResponse])
def list_missions(
    project_id: UUID = Query(...),
    status: MissionStatus | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    _ensure_project_access(db, project_id, current_user)

    query = db.query(Mission).filter(Mission.project_id == project_id)
    if status is not None:
        query = query.filter(Mission.status == status.value)
    if search:
        query = query.filter(Mission.intent.ilike(f"%{search}%"))

    missions = query.order_by(Mission.updated_at.desc()).offset(offset).limit(limit).all()

    result = []
    for m in missions:
        task = db.query(Task).filter(Task.mission_id == m.id).first()
        result.append({
            "id": m.id,
            "project_id": m.project_id,
            "intent": m.intent,
            "status": m.status,
            "task": {
                "id": task.id if task else None,
                "mission_id": m.id,
                "name": task.name if task else "unknown",
                "status": task.status if task else "CREATED",
                "result": task.result_json if task else None,
                "error": task.error if task else None
            },
            "execution_mode": m.execution_mode,
            "created_at": m.created_at
        })
    return result


@router.get("/api/v1/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    _ensure_project_access(db, project_id, current_user)

    missions = db.query(Mission).filter(Mission.project_id == project_id).all()

    running = sum(m.status == MissionStatus.RUNNING.value for m in missions)
    completed = sum(m.status == MissionStatus.COMPLETED.value for m in missions)
    failed = sum(m.status == MissionStatus.FAILED.value for m in missions)
    blocked = sum(m.status == MissionStatus.BLOCKED.value for m in missions)

    recent_missions = sorted(missions, key=lambda m: m.created_at, reverse=True)[:5]
    recent_formatted = []

    for m in recent_missions:
        task = db.query(Task).filter(Task.mission_id == m.id).first()
        recent_formatted.append({
            "id": m.id,
            "project_id": m.project_id,
            "intent": m.intent,
            "status": m.status,
            "task": {
                "id": task.id if task else None,
                "mission_id": m.id,
                "name": task.name if task else "unknown",
                "status": task.status if task else "CREATED",
                "result": task.result_json if task else None,
                "error": task.error if task else None
            },
            "execution_mode": m.execution_mode,
            "created_at": m.created_at
        })

    return {
        "project_id": project_id,
        "total_missions": len(missions),
        "running_missions": running,
        "completed_missions": completed,
        "failed_missions": failed,
        "blocked_missions": blocked,
        "recent_missions": recent_formatted,
    }


@router.get("/api/v1/projects/{project_id}/artifacts")
def list_project_artifacts(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    _ensure_project_access(db, project_id, current_user)
    artifacts = db.query(Artifact).filter(Artifact.project_id == project_id).order_by(Artifact.created_at.desc()).all()
    return [
        {
            "id": artifact.id,
            "name": artifact.name,
            "type": artifact.type,
            "mime_type": artifact.mime_type,
            "size_bytes": artifact.size_bytes,
            "status": artifact.status,
            "created_at": artifact.created_at,
            "mission_id": artifact.mission_id,
            "task_id": artifact.task_id,
        }
        for artifact in artifacts
    ]


@router.get("/api/v1/projects/{project_id}/evidence")
def list_project_evidence(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    _ensure_project_access(db, project_id, current_user)
    evidence = (
        db.query(Evidence)
        .join(Mission, Evidence.mission_id == Mission.id)
        .filter(Mission.project_id == project_id)
        .order_by(Evidence.created_at.desc())
        .all()
    )
    return [
        {
            "id": record.id,
            "mission_id": record.mission_id,
            "task_id": record.task_id,
            "source": record.source,
            "label": record.label,
            "quote": record.quote,
            "confidence": record.confidence,
            "created_at": record.created_at,
        }
        for record in evidence
    ]


@router.get("/api/v1/missions/{mission_id}", response_model=MissionDetailResponse)
def get_mission_detail(
    mission_id: UUID,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    _ensure_project_access(db, project_id, current_user)

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.project_id == project_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    task = db.query(Task).filter(Task.mission_id == mission.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")

    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).all()
    return _format_mission(mission, task, events, db)


@router.post("/api/v1/missions/{mission_id}/actions/{action}", response_model=MissionDetailResponse)
def control_mission(
    mission_id: UUID,
    action: str,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Apply an explicit lifecycle action; invalid state changes are rejected."""
    _ensure_project_access(db, project_id, current_user)
    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.project_id == project_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")
    task = db.query(Task).filter(Task.mission_id == mission.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="TASK_NOT_FOUND")

    orchestrator = MissionOrchestrator()
    normalized = action.casefold()
    try:
        if normalized == "pause":
            orchestrator._set_mission_status(mission, MissionStatus.PAUSED)
            orchestrator.record_event(db, mission, "MISSION_PAUSED", "Execution paused by an authorized user.")
        elif normalized == "resume":
            orchestrator._set_mission_status(mission, MissionStatus.RUNNING)
            orchestrator.record_event(db, mission, "MISSION_RESUMED", "Execution resumed by an authorized user.")
            orchestrator.execute(db, mission=mission, task=task, user=current_user)
        elif normalized == "cancel":
            current = MissionStatus(mission.status)
            if current in {MissionStatus.REQUESTED, MissionStatus.DRAFT, MissionStatus.VALIDATING, MissionStatus.PLANNED, MissionStatus.WAITING_FOR_INPUT, MissionStatus.WAITING_FOR_APPROVAL, MissionStatus.READY, MissionStatus.APPROVED}:
                orchestrator._set_mission_status(mission, MissionStatus.CANCELLED)
            else:
                orchestrator._set_mission_status(mission, MissionStatus.CANCELLING)
                orchestrator._set_mission_status(mission, MissionStatus.CANCELLED)
            if TaskStatus(task.status) not in {TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
                orchestrator._set_task_status(task, TaskStatus.CANCELLED)
            orchestrator.record_event(db, mission, "MISSION_CANCELLED", "Execution cancelled by an authorized user.")
        elif normalized == "retry":
            if MissionStatus(mission.status) not in {MissionStatus.FAILED, MissionStatus.TIMED_OUT, MissionStatus.BLOCKED}:
                raise ValueError("MISSION_RETRY_NOT_ALLOWED")
            # A retry is a new immutable version of the existing request,
            # avoiding an illegal transition out of a terminal run.
            raise HTTPException(status_code=409, detail="MISSION_RETRY_CREATES_NEW_VERSION")
        else:
            raise HTTPException(status_code=422, detail="MISSION_ACTION_UNSUPPORTED")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    db.commit()
    db.refresh(mission)
    db.refresh(task)
    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).order_by(LifecycleEvent.created_at).all()
    return _format_mission(mission, task, events, db)


@router.get("/api/v1/missions/{mission_id}/tasks", response_model=list[dict])
def get_mission_tasks(
    mission_id: UUID,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    _ensure_project_access(db, project_id, current_user)

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.project_id == project_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    tasks = db.query(Task).filter(Task.mission_id == mission_id).all()
    return [
        {
            "id": t.id,
            "mission_id": t.mission_id,
            "name": t.name,
            "status": t.status,
            "result": t.result_json,
            "error": t.error,
        }
        for t in tasks
    ]


@router.get("/api/v1/missions/{mission_id}/events")
def get_mission_events(
    mission_id: UUID,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    _ensure_project_access(db, project_id, current_user)

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.project_id == project_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission_id).order_by(LifecycleEvent.created_at).all()
    return [
        {
            "id": e.id,
            "mission_id": e.mission_id,
            "event_type": e.event_type,
            "timestamp": e.updated_at,
            "detail": e.detail,
        }
        for e in events
    ]


@router.get("/api/v1/missions/{mission_id}/explanation-report")
def get_explanation_report(
    mission_id: UUID,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db)
):
    _ensure_project_access(db, project_id, current_user)

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.project_id == project_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    result = mission.metadata_json.get("result", {}) if mission.metadata_json else {}
    profile = {"execution_mode": mission.execution_mode, "model_mode": "AUTO"}

    summary = {
        "mission_id": str(mission.id),
        "project_id": str(mission.project_id),
        "execution_mode": profile.get("execution_mode", mission.execution_mode),
        "model_mode": profile.get("model_mode", "AUTO"),
        "workflow": "resume_jd_intelligence_v1",
        "steps": [
            "Intent captured",
            "Resume and JD parsed",
            "Skill alignment computed",
            "Validation and evidence checks applied",
            "Artifact report generated",
        ],
        "status": mission.status,
        "summary": result.get("match_analysis", {}).get("score_explanation", "No structured match analysis available."),
        "why_selected": "The bounded workflow is the minimum sufficient strategy for resume/JD comparison.",
    }

    task = db.query(Task).filter(Task.mission_id == mission.id).first()

    return {
        "mission_id": mission.id,
        "project_id": mission.project_id,
        "summary": summary,
        "execution_steps": [
            {"step": "intent_capture", "status": "SUCCEEDED", "detail": mission.intent},
            {"step": "document_parsing", "status": task.status if task else "UNKNOWN", "detail": "Parsed resume and job description text."},
            {"step": "match_validation", "status": "SUCCEEDED", "detail": result.get("match_analysis", {}).get("overall_match_score", 0)},
        ],
        "evidence": result.get("evidence", []),
        "artifacts": [{"artifact_type": "resume_jd_match_report", "version": "v1", "status": "CREATED"}],
        "created_at": mission.created_at,
    }
