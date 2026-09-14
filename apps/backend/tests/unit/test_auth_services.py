from uuid import uuid4

from app.services.auth import AuthService


def test_auth_service_registers_and_authenticates_user() -> None:
    service = AuthService(path=":memory:")
    user = service.register_user("Alice Example", "alice@example.com", "SecurePass123!")

    assert user["email"] == "alice@example.com"
    assert service.authenticate_user("alice@example.com", "SecurePass123!") is not None
    assert service.authenticate_user("alice@example.com", "wrong-pass") is None


def test_auth_service_creates_project_with_member_access() -> None:
    service = AuthService(path=":memory:")
    user = service.register_user("Bob User", "bob@example.com", "SecurePass123!")
    project = service.create_project(str(user["id"]), "Alpha Project")

    assert project["name"] == "Alpha Project"
    assert str(user["id"]) in project["members"]
    assert service.user_has_project_access(str(user["id"]), project["id"]) is True
