from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def _register(client, email, password):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_auth_registration_login_and_project_isolation(client) -> None:
    user_a = _register(client, f"alice-{uuid4()}@example.com", "secretpass123")
    user_b = _register(client, f"bob-{uuid4()}@example.com", "secretpass123")

    token_a = client.post(
        "/api/v1/auth/login",
        json={"email": user_a["email"], "password": "secretpass123"},
    ).json()["access_token"]
    token_b = client.post(
        "/api/v1/auth/login",
        json={"email": user_b["email"], "password": "secretpass123"},
    ).json()["access_token"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Alpha"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]

    mission = client.post(
        "/api/v1/missions/resume-jd",
        json={
            "project_id": project_id,
            "resume_text": "Python SQL",
            "job_description": "Python Kubernetes",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert mission.status_code == 201, mission.text


def test_execution_profile_is_returned(client) -> None:
    user = _register(client, f"charlie-{uuid4()}@example.com", "secretpass123")
    token = client.post(
        "/api/v1/auth/login",
        json={"email": user["email"], "password": "secretpass123"},
    ).json()["access_token"]

    project = client.post(
        "/api/v1/projects",
        json={"name": "Beta"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    mission = client.post(
        "/api/v1/missions/resume-jd",
        json={
            "project_id": project["id"],
            "resume_text": "Python SQL experience",
            "job_description": "Python Kubernetes required",
            "execution_profile": {
                "execution_mode": "GUIDED",
                "model_mode": "HIGH_QUALITY",
                "preferred_provider": "openai",
                "allowed_capabilities": ["DOCUMENT_PARSE", "REPORT_GENERATION"],
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert mission.status_code == 201, mission.text
    assert mission.json()["status"] == "COMPLETED"
