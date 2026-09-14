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
from app.models.base import User, Project, Mission, Task, LifecycleEvent, ProjectMember
from app.utils.text import ParsedDocument, parse_document
from app.repositories.projects import project_repo
from app.capabilities.resume_jd.service import analyze_resume_against_jd
from app.capabilities.resume_jd.parser import build_analysis, validate_analysis
from app.execution.task_state import validate_transition
from app.api.deps import DEFAULT_DEMO_USER_ID
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.broker import AgentRegistry, AgentHarness

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


def _format_mission(mission: Mission, task: Task, events: list[LifecycleEvent]) -> dict:
    formatted_events = [
        MissionEventResponse(
            id=e.id,
            mission_id=e.mission_id,
            event_type=e.event_type,
            timestamp=e.updated_at,
            detail=e.detail
        ) for e in events
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
        "created_at": mission.created_at,
        "updated_at": mission.updated_at,
        "completed_at": mission.completed_at,
        "events": formatted_events,
        "approvals": []
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
    prompt_lower = request.prompt.lower()
    
    # Simple Mock Intent Gate routing
    slug = "rag"
    agent_id = "manager_agent"
    
    if "research" in prompt_lower or "framework" in prompt_lower:
        slug = "research"
        agent_id = "research_agent"
    elif "analyze" in prompt_lower or "csv" in prompt_lower or "data" in prompt_lower:
        slug = "data_analysis"
        agent_id = "data_analyst_agent"
    elif "code" in prompt_lower or "flask" in prompt_lower or "python" in prompt_lower:
        slug = "code_analysis"
        agent_id = "coding_agent"
    elif "report" in prompt_lower or "presentation" in prompt_lower:
        slug = "report_generation"
        agent_id = "report_agent"
    elif "learn" in prompt_lower or "roadmap" in prompt_lower:
        slug = "learning"
        agent_id = "manager_agent"
        
    registry = CapabilityRegistry()
    agents = AgentRegistry()
    capability = registry.get(slug)
    agent_def = agents.get(agent_id)
    
    mission = Mission(
        project_id=project.id,
        intent=request.prompt,
        status=MissionStatus.COMPLETED.value,
        execution_mode=request.execution_profile.execution_mode if request.execution_profile else "AUTO",
    )
    db.add(mission)
    db.flush()

    task = Task(mission_id=mission.id, name=f"run_{slug}", status=TaskStatus.SUCCEEDED.value)
    db.add(task)
    db.flush()

    _record_event(db, mission, "MISSION_CREATED", f"Universal mission created matching '{capability.name}'.")
    _record_event(db, mission, "AGENT_ASSIGNED", f"Assigned to {agent_def.name}.")
    _record_event(db, mission, "MISSION_COMPLETED", "Task successfully completed by agent.")
    
    mission.metadata_json = {
        "result": {
            "output": f"Mock output from {agent_def.name} executing capability {capability.name}.",
            "agent": agent_def.name,
            "capability": capability.name,
            "risk_level": capability.risk_level.name,
            "tools_used": list(agent_def.tool_allowlist)
        }
    }
    task.result_json = mission.metadata_json["result"]
    mission.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(mission)
    db.refresh(task)
    
    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).all()
    return _format_mission(mission, task, events)


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
    return _format_mission(mission, task, events)


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
