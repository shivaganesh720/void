from unittest.mock import patch
from uuid import uuid4
from fastapi.testclient import TestClient

def test_create_universal_mission_routing(client: TestClient, db_session):
    project_id = str(uuid4())
    
    # 1. Test Research Intent
    res = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": project_id,
            "prompt": "Research the latest framework",
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert "Mock output from Research Agent" in data["result"]["output"]

    # 2. Test Data Analysis Intent
    res2 = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": project_id,
            "prompt": "Analyze this csv data",
        }
    )
    assert res2.status_code == 201
    assert "Data Analyst Agent" in res2.json()["result"]["agent"]

    # 3. Test Invalid Project Access (Demo User Auto-Provisions)
    other_project = str(uuid4())
    res3 = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": other_project,
            "prompt": "Unknown task",
        }
    )
    assert res3.status_code == 201
    assert "Manager / Supervisor Agent" in res3.json()["result"]["agent"]
