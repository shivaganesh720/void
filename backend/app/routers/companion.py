from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.api.deps import get_db

router = APIRouter(prefix="/api/v1/companion", tags=["Companion"])

class DeviceRegistration(BaseModel):
    device_name: str
    os_type: str
    capabilities: list[str]

@router.post("/register")
def register_companion(device: DeviceRegistration, db: Session = Depends(get_db)):
    """
    Register a local Windows companion device.
    In a real implementation, this issues a secure connection token and saves to the DB.
    """
    return {
        "status": "registered",
        "device_id": "local-win-companion-1",
        "token": "mock-secure-websocket-token"
    }

@router.websocket("/ws")
async def companion_websocket(websocket: WebSocket):
    """
    Secure WebSocket for the Local Windows Companion to receive tasks.
    """
    await websocket.accept()
    try:
        while True:
            # Companion heartbeat or telemetry
            data = await websocket.receive_json()
            if data.get("type") == "heartbeat":
                await websocket.send_json({"type": "ack", "status": "active"})
    except WebSocketDisconnect:
        # Handle cleanup
        pass
