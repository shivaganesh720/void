from uuid import uuid4

from fastapi.testclient import TestClient

from app.contracts.enums import MissionStatus, TaskStatus
from app.main import MISSIONS, StoredMission, StoredTask, app


def test_approval_request_and_decision_flow() -> None:
    client = TestClient(app)
    mission_id = uuid4()
    project_id = uuid4()
    task = StoredTask(id=uuid4(), mission_id=mission_id, name="resume_jd_analysis", status=TaskStatus.CREATED)
    mission = StoredMission(
        id=mission_id,
        project_id=project_id,
        intent="Review protected content",
        status=MissionStatus.WAITING_FOR_APPROVAL,
        task=task,
        approval_required=True,
    )
    MISSIONS[mission_id] = mission

    approval_response = client.post(
        f"/api/v1/missions/{mission_id}/approvals",
        params={"project_id": str(project_id)},
        json={
            "requested_action": "Run private model review",
            "risk_reason": "Private resume data requires review",
            "required_by_policy": True,
            "reviewer_id": "human-reviewer-1",
        },
    )

    assert approval_response.status_code == 201, approval_response.text
    approval = approval_response.json()
    assert approval["status"] == "PENDING"

    decision_response = client.patch(
        f"/api/v1/missions/{mission_id}/approvals/{approval['id']}",
        params={"project_id": str(project_id)},
        json={
            "decision": "APPROVED",
            "reviewer_id": "human-reviewer-1",
            "reviewer_comment": "Approved for execution.",
        },
    )

    assert decision_response.status_code == 200, decision_response.text
    payload = decision_response.json()
    assert payload["status"] == "APPROVED"
    assert payload["mission_id"] == str(mission_id)
