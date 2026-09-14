from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from uuid import UUID

router = APIRouter(tags=["streaming"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, mission_id: UUID):
        await websocket.accept()
        if mission_id not in self.active_connections:
            self.active_connections[mission_id] = []
        self.active_connections[mission_id].append(websocket)

    def disconnect(self, websocket: WebSocket, mission_id: UUID):
        if mission_id in self.active_connections:
            self.active_connections[mission_id].remove(websocket)
            if not self.active_connections[mission_id]:
                del self.active_connections[mission_id]

    async def broadcast_to_mission(self, message: str, mission_id: UUID):
        if mission_id in self.active_connections:
            for connection in self.active_connections[mission_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/api/v1/ws/missions/{mission_id}")
async def websocket_endpoint(websocket: WebSocket, mission_id: UUID):
    await manager.connect(websocket, mission_id)
    try:
        while True:
            data = await websocket.receive_text()
            # This is a one-way event stream from server to client,
            # but we read to keep the connection alive and handle disconnects.
            await manager.broadcast_to_mission(f"Echo: {data}", mission_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, mission_id)
