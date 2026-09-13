from app.governance.audit import AuditLogService


def test_audit_log_service_records_and_filters_events() -> None:
    service = AuditLogService(path=":memory:")
    first = service.record_event(project_id="project-1", actor_id="user-1", event_type="MISSION_STARTED", payload={"mission_id": "m-1"})
    second = service.record_event(project_id="project-1", actor_id="admin-user", event_type="APPROVAL_GRANTED", payload={"mission_id": "m-1"})

    assert first["event_type"] == "MISSION_STARTED"
    assert second["actor_id"] == "admin-user"
    assert service.filter_events(project_id="project-1")
    assert service.filter_events(actor_id="admin-user")
