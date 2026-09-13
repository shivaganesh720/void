"""Admin policy and route tests – updated for SQLAlchemy-backed routers."""
import pytest
from uuid import uuid4

from app.governance.admin import AdminAccessPolicy, Role


def test_admin_policy_uses_role_not_hardcoded_user() -> None:
    policy = AdminAccessPolicy()
    assert policy.can_access("ADMIN", Role.ADMIN) is True
    assert policy.can_access("AUDITOR", Role.AUDITOR) is True
    assert policy.can_access("USER", Role.ADMIN) is False
    assert policy.evaluate("ADMIN", Role.ADMIN).allowed is True


def _register_and_promote(client, db, email: str, role: str) -> dict:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass!123", "full_name": "Admin Tester"},
    )
    assert resp.status_code == 201
    user_data = resp.json()

    from app.db.base import User
    from uuid import UUID
    user = db.query(User).filter(User.id == UUID(user_data["id"])).first()
    user.role = role
    db.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    return login.json()


def test_admin_overview_requires_admin_role(client) -> None:
    from app.main import app
    from app.api.deps import get_db
    db = next(app.dependency_overrides[get_db]())

    email = f"admin-overview-{uuid4()}@example.com"
    token_data = _register_and_promote(client, db, email, "ADMIN")
    token = token_data["access_token"]

    overview_response = client.get("/api/v1/admin/overview", headers={"Authorization": f"Bearer {token}"})
    assert overview_response.status_code == 200, overview_response.text
    payload = overview_response.json()
    assert payload["user_count"] >= 1
    assert payload["admin_count"] >= 1
    db.close()


def test_admin_users_listing_requires_admin_role(client) -> None:
    from app.main import app
    from app.api.deps import get_db
    db = next(app.dependency_overrides[get_db]())

    email = f"admin-users-{uuid4()}@example.com"
    token_data = _register_and_promote(client, db, email, "ADMIN")
    token = token_data["access_token"]

    users_response = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert users_response.status_code == 200, users_response.text
    payload = users_response.json()
    assert isinstance(payload, list)
    assert any(item["email"] == email for item in payload)
    db.close()
