from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from app.contracts.enums import MissionStatus
from app.control_plane.engine import StrategyResolver
from app.repositories.missions import MissionRepository


class MissionService:
    def __init__(self, path: str = ".local/void-missions.sqlite3") -> None:
        self.repo = MissionRepository(path=path)
        self.resolver = StrategyResolver()

    def create_mission(self, *, project_id, intent: str, status: MissionStatus = MissionStatus.DRAFT) -> dict:
        mission_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        decision = self.resolver.resolve(intent)
        payload = {
            "id": mission_id,
            "project_id": str(project_id),
            "intent": intent,
            "status": status.value,
            "blueprint": {
                "mission_id": mission_id,
                "strategy": decision.strategy.value,
                "workflow_id": decision.workflow_id,
                "steps": ["normalize_intent", "validate_inputs", "execute_strategy", "validate_output"],
            },
            "task": {
                "id": str(uuid4()),
                "name": "mission_execution",
                "status": "CREATED",
            },
            "created_at": now,
            "updated_at": now,
        }
        self.repo.save_mission(payload)
        return payload

    def update_status(self, mission_id: str, status: MissionStatus) -> dict:
        mission = self.repo.get_mission(mission_id)
        if mission is None:
            raise KeyError(f"MISSION_NOT_FOUND:{mission_id}")
        mission["status"] = status.value
        mission["updated_at"] = datetime.now(UTC).isoformat()
        self.repo.save_mission(mission)
        return mission

    def pause_mission(self, mission_id: str) -> dict:
        mission = self.repo.get_mission(mission_id)
        if mission is None:
            raise KeyError(f"MISSION_NOT_FOUND:{mission_id}")
        mission["status"] = MissionStatus.PAUSED.value
        mission["updated_at"] = datetime.now(UTC).isoformat()
        self.repo.save_mission(mission)
        return mission

    def resume_mission(self, mission_id: str) -> dict:
        mission = self.repo.get_mission(mission_id)
        if mission is None:
            raise KeyError(f"MISSION_NOT_FOUND:{mission_id}")
        mission["status"] = MissionStatus.RUNNING.value
        mission["updated_at"] = datetime.now(UTC).isoformat()
        self.repo.save_mission(mission)
        return mission

    def cancel_mission(self, mission_id: str) -> dict:
        mission = self.repo.get_mission(mission_id)
        if mission is None:
            raise KeyError(f"MISSION_NOT_FOUND:{mission_id}")
        mission["status"] = MissionStatus.CANCELLED.value
        mission["updated_at"] = datetime.now(UTC).isoformat()
        self.repo.save_mission(mission)
        return mission

    def retry_mission(self, mission_id: str) -> dict:
        mission = self.repo.get_mission(mission_id)
        if mission is None:
            raise KeyError(f"MISSION_NOT_FOUND:{mission_id}")
        mission["status"] = MissionStatus.RUNNING.value
        mission["updated_at"] = datetime.now(UTC).isoformat()
        self.repo.save_mission(mission)
        return mission

    def recover_mission(self, mission_id: str) -> dict:
        mission = self.repo.get_mission(mission_id)
        if mission is None:
            raise KeyError(f"MISSION_NOT_FOUND:{mission_id}")
        if mission["status"] in {MissionStatus.CANCELLED.value, MissionStatus.FAILED.value}:
            mission["status"] = MissionStatus.DRAFT.value
        else:
            mission["status"] = MissionStatus.RUNNING.value
        mission["updated_at"] = datetime.now(UTC).isoformat()
        self.repo.save_mission(mission)
        return mission
