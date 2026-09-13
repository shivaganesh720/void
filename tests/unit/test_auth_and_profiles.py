from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def _register(client, email, password):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_auth_registration_login_and_project_isolation() -> None:
    client = TestClient(app)
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
    mission_id = mission.json()["id"]

    forbidden = client.get(
        f"/api/v1/missions/{mission_id}",
        params={"project_id": project_id},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert forbidden.status_code in {403, 404}, forbidden.text


def test_execution_profile_and_explanation_report_are_returned() -> None:
    client = TestClient(app)
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
    mission_id = mission.json()["id"]

    report = client.get(
        f"/api/v1/missions/{mission_id}/explanation-report",
        params={"project_id": project["id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert report.status_code == 200, report.text
    payload = report.json()
    assert payload["mission_id"] == mission_id
    assert payload["summary"]["execution_mode"] in {"AUTO", "GUIDED", "MANUAL"}
    assert "workflows" in payload["summary"] or "steps" in payload["summary"]
