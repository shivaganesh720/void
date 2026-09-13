from app.services.project_access import ProjectAccessService


def test_project_access_service_enforces_membership_and_ownership() -> None:
    service = ProjectAccessService()
    service.register_project(project_id="project-1", owner_id="owner-1", members=["member-1"])

    assert service.user_has_project_access(user_id="owner-1", project_id="project-1") is True
    assert service.user_has_project_access(user_id="member-1", project_id="project-1") is True
    assert service.user_has_project_access(user_id="member-2", project_id="project-1") is False

    assert service.require_owner(user_id="owner-1", project_id="project-1").project_owner_id == "owner-1"

    try:
        service.require_owner(user_id="member-1", project_id="project-1")
        assert False, "expected PermissionError"
    except PermissionError:
        pass
