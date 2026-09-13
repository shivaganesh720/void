from app.contracts.enums import MissionStatus
from app.services.missions import MissionService


def test_mission_service_tracks_lifecycle_and_recovery() -> None:
    service = MissionService(path=":memory:")
    mission = service.create_mission(project_id="project-1", intent="Review a document for risks")

    updated = service.pause_mission(mission["id"])
    assert updated["status"] == MissionStatus.PAUSED.value

    resumed = service.resume_mission(mission["id"])
    assert resumed["status"] == MissionStatus.RUNNING.value

    cancelled = service.cancel_mission(mission["id"])
    assert cancelled["status"] == MissionStatus.CANCELLED.value

    recovered = service.recover_mission(mission["id"])
    assert recovered["status"] in {MissionStatus.CANCELLED.value, MissionStatus.DRAFT.value}


def test_mission_service_retries_failed_missions() -> None:
    service = MissionService(path=":memory:")
    mission = service.create_mission(project_id="project-2", intent="Analyze metrics")
    service.update_status(mission["id"], MissionStatus.FAILED)

    retried = service.retry_mission(mission["id"])
    assert retried["status"] == MissionStatus.RUNNING.value
