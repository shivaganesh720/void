from fastapi.testclient import TestClient

from app.main import app


def test_liveness_endpoint() -> None:
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_resume_jd_mission_executes_and_is_retrievable() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/missions/resume-jd",
        json={
            "resume_text": "Python SQL experience",
            "job_description": "Python SQL Kubernetes required",
        },
    )

    assert response.status_code == 201
    mission = response.json()
    assert mission["status"] == "COMPLETED"
    assert mission["task"]["status"] == "SUCCEEDED"
    assert "kubernetes" in mission["result"]["missing_skills"]

    retrieved = client.get(f"/api/v1/missions/{mission['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["result"] == mission["result"]


def test_resume_jd_mission_rejects_missing_resume() -> None:
    response = TestClient(app).post(
        "/api/v1/missions/resume-jd",
        json={"resume_text": "", "job_description": "Python required"},
    )

    assert response.status_code == 422