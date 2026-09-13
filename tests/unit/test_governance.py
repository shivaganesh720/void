from app.governance.admin import AdminAccessPolicy, Role
from app.governance.observability import ObservabilityRecord, ObservabilityService, RetentionPolicy


def test_admin_access_policy_enforces_roles() -> None:
    policy = AdminAccessPolicy()
    assert policy.can_access("admin-user", Role.ADMIN) is True
    assert policy.can_access("regular-user", Role.ADMIN) is False


def test_observability_service_records_metrics_and_events() -> None:
    service = ObservabilityService()
    rec = service.record_event("mission.started", {"mission_id": "m-1"}, actor_id="user-42")
    metric = service.record_metric("missions.completed", 1)

    assert rec.event_type == "mission.started"
    assert metric["name"] == "missions.completed"
    assert service.latest_event()["event_type"] == "mission.started"


def test_retention_policy_flags_expired_records() -> None:
    policy = RetentionPolicy(days_to_live=30)
    expired = policy.should_expire(days_old=31)
    active = policy.should_expire(days_old=10)

    assert expired is True
    assert active is False
