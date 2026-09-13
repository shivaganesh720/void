from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_registration_profile_and_logout_journey() -> None:
    client = TestClient(app)
    email = f"journey-{uuid4()}@example.com"
    registered = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Journey User", "email": email, "password": "SecurePass123"},
    )
    assert registered.status_code == 201
    assert registered.json()["onboarding_completed"] is False

    login = client.post("/api/v1/auth/login", json={"email": email, "password": "SecurePass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.patch(
        "/api/v1/auth/profile",
        headers=headers,
        json={
            "ai_awareness": "AI_AWARE",
            "default_mode": "GUIDED",
            "explanation_level": "TECHNICAL",
            "execution_priority": "PRIVACY",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["onboarding_completed"] is True

    current = client.get("/api/v1/auth/me", headers=headers)
    assert current.status_code == 200
    assert current.json()["full_name"] == "Journey User"

    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
