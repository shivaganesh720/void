from uuid import uuid4

from app.contracts.enums import MissionStatus
from app.repositories.missions import MissionRepository
from app.services.missions import MissionService


def test_mission_repository_persists_and_loads() -> None:
    repo = MissionRepository(path=":memory:")
    mission_id = uuid4()
    project_id = uuid4()

    repo.save_mission({
        "id": str(mission_id),
        "project_id": str(project_id),
        "intent": "Analyze candidate fit",
        "status": MissionStatus.DRAFT.value,
        "task": {"id": str(uuid4()), "name": "review", "status": MissionStatus.DRAFT.value},
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    })

    loaded = repo.list_by_project(str(project_id))
    assert len(loaded) == 1
    assert loaded[0]["intent"] == "Analyze candidate fit"


def test_mission_service_builds_blueprint_and_updates_status() -> None:
    service = MissionService(path=":memory:")
    project_id = uuid4()
    mission = service.create_mission(project_id=project_id, intent="Compare my resume with that job description")

    assert mission["status"] == MissionStatus.DRAFT.value
    assert mission["blueprint"]["strategy"] == "RESEARCH_AND_VALIDATE"

    updated = service.update_status(mission["id"], MissionStatus.VALIDATING)
    assert updated["status"] == MissionStatus.VALIDATING.value
