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
    assert data["status"] == "WAITING_FOR_APPROVAL"
    approval = data["approvals"][0]
    approval_response = client.patch(
        f"/api/v1/missions/{data['id']}/approvals/{approval['id']}?project_id={project_id}",
        json={"decision": "APPROVED"},
    )
    assert approval_response.status_code == 200
    assert approval_response.json()["status"] == "APPROVED"

    mission = client.get(f"/api/v1/missions/{data['id']}?project_id={project_id}")
    assert mission.status_code == 200
    assert mission.json()["status"] == "COMPLETED"
    assert mission.json()["result"]["provider"]["local_fallback"] is True

    # 2. Test Data Analysis Intent
    res2 = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": project_id,
            "prompt": "Analyze this csv data",
        }
    )
    assert res2.status_code == 201
    assert res2.json()["status"] == "WAITING_FOR_INPUT"

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
    assert res3.json()["status"] == "COMPLETED"
    assert res3.json()["result"]["agent"]["name"] == "Manager / Supervisor Agent"
