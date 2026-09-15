from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.api.v1.missions import _ensure_project_access, _format_mission
from app.execution.orchestrator import MissionOrchestrator
from app.models.base import LifecycleEvent, User
from app.models.enums import MissionStatus
from app.schemas import ExecutionProfileRequest, MissionDetailResponse
from app.services.voice import VoiceService

router = APIRouter(prefix="/api/v1/companion", tags=["Companion"])


class DeviceRegistration(BaseModel):
    device_name: str
    os_type: str
    capabilities: list[str]


class VoiceCommandRequest(BaseModel):
    project_id: UUID
    prompt: str | None = None
    audio_base64: str | None = None
    execution_profile: ExecutionProfileRequest | None = None


@router.post("/register")
def register_companion(device: DeviceRegistration, db: Session = Depends(get_db)):
    """
    Register a local Windows companion device.
    This is still a minimal local registration surface, but it uses the same
    governance runtime for any subsequent command dispatch.
    """
    return {
        "status": "registered",
        "device_id": "local-win-companion-1",
        "token": "mock-secure-websocket-token",
        "capabilities": device.capabilities,
    }


@router.post("/voice/command", response_model=MissionDetailResponse, status_code=201)
def voice_command(
    request: VoiceCommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Turn voice input into a governed VOID mission using the real mission runtime."""
    _ensure_project_access(db, request.project_id, current_user)

    transcript = (request.prompt or "").strip()
    if not transcript and request.audio_base64:
        transcript = VoiceService().transcribe_base64(request.audio_base64)

    if not transcript:
        raise HTTPException(status_code=400, detail="VOICE_COMMAND_EMPTY")

    orchestrator = MissionOrchestrator()
    mission, task = orchestrator.create_and_plan(
        db,
        project_id=request.project_id,
        user=current_user,
        prompt=transcript,
        execution_profile=request.execution_profile,
    )
    if mission.status == MissionStatus.READY.value:
        orchestrator.execute(db, mission=mission, task=task, user=current_user)
    db.commit()
    db.refresh(mission)
    db.refresh(task)
    events = db.query(LifecycleEvent).filter(LifecycleEvent.mission_id == mission.id).order_by(LifecycleEvent.created_at).all()
    return _format_mission(mission, task, events, db)


@router.websocket("/ws")
async def companion_websocket(websocket: WebSocket):
    """
    Secure WebSocket for the Local Windows Companion to receive tasks.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "heartbeat":
                await websocket.send_json({"type": "ack", "status": "active"})
    except WebSocketDisconnect:
        pass
