from uuid import uuid4

from app.main import app


def test_registration_profile_and_logout_journey(client) -> None:
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


def test_refresh_token_rotation_and_reuse_detection(client) -> None:
    email = f"refresh-{uuid4()}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Refresh User", "email": email, "password": "SecurePass123"},
    )

    login = client.post("/api/v1/auth/login", json={"email": email, "password": "SecurePass123"})
    assert login.status_code == 200, login.text
    payload = login.json()
    assert "refresh_token" in payload

    refresh = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
        json={"refresh_token": payload["refresh_token"]},
    )
    assert refresh.status_code == 200, refresh.text
    rotated = refresh.json()
    assert rotated["user_id"] == payload["user_id"]
    assert rotated["access_token"] != payload["access_token"]
    assert rotated["refresh_token"] != payload["refresh_token"]

    replay = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
        json={"refresh_token": payload["refresh_token"]},
    )
    assert replay.status_code == 401, replay.text
