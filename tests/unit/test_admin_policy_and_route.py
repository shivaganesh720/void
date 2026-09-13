from uuid import uuid4

from fastapi.testclient import TestClient

from app.governance.admin import AdminAccessPolicy, Role
from app.main import app


def test_admin_policy_uses_role_not_hardcoded_user() -> None:
    policy = AdminAccessPolicy()
    assert policy.can_access("ADMIN", Role.ADMIN) is True
    assert policy.can_access("AUDITOR", Role.AUDITOR) is True
    assert policy.can_access("USER", Role.ADMIN) is False
    assert policy.evaluate("ADMIN", Role.ADMIN).allowed is True


def test_admin_overview_requires_admin_role() -> None:
    client = TestClient(app)
    email = f"admin-overview-{uuid4()}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass!123", "full_name": "Admin Overview"},
    )
    assert register_response.status_code == 201, register_response.text
    user_id = register_response.json()["id"]

    from app.main import USERS
    from uuid import UUID

    USERS[UUID(user_id)].role = "ADMIN"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]

    overview_response = client.get("/api/v1/admin/overview", headers={"Authorization": f"Bearer {token}"})
    assert overview_response.status_code == 200, overview_response.text
    payload = overview_response.json()
    assert payload["user_count"] >= 1
    assert payload["admin_count"] >= 1


def test_admin_users_listing_requires_admin_role() -> None:
    client = TestClient(app)
    email = f"admin-users-{uuid4()}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass!123", "full_name": "Admin User Viewer"},
    )
    assert register_response.status_code == 201, register_response.text
    user_id = register_response.json()["id"]

    from app.main import USERS
    from uuid import UUID

    USERS[UUID(user_id)].role = "ADMIN"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]

    users_response = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert users_response.status_code == 200, users_response.text
    payload = users_response.json()
    assert isinstance(payload, list)
    assert any(item["email"] == email for item in payload)
