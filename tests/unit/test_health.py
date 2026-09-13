from fastapi.testclient import TestClient

from app.main import app


def test_liveness_endpoint(client) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_resume_jd_mission_executes_and_is_retrievable(client) -> None:
    project_id = "00000000-0000-0000-0000-000000000001"
    response = client.post(
        "/api/v1/missions/resume-jd",
        json={
            "project_id": project_id,
            "resume_text": "Python SQL experience",
            "job_description": "Python SQL Kubernetes required",
        },
    )

    assert response.status_code == 201
    mission = response.json()
    assert mission["status"] == "COMPLETED"
    assert mission["task"]["status"] == "SUCCEEDED"
    assert "kubernetes" in mission["result"]["missing_skills"]

    listed = client.get(f"/api/v1/missions?project_id={project_id}")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == mission["id"]

    summary = client.get(f"/api/v1/dashboard/summary?project_id={project_id}")
    assert summary.status_code == 200
    assert summary.json()["completed_missions"] >= 1
    assert summary.json()["blocked_missions"] == 0


def test_resume_jd_mission_rejects_missing_resume(client) -> None:
    response = client.post(
        "/api/v1/missions/resume-jd",
        json={"resume_text": "", "job_description": "Python required"},
    )

    assert response.status_code == 422