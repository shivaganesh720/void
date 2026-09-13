"""Approval tests – now using the SQLAlchemy-backed approvals router."""
from uuid import uuid4


def test_approval_request_and_decision_flow(client) -> None:
    # First create a mission
    project_id = "00000000-0000-0000-0000-000000000001"
    mission_resp = client.post(
        "/api/v1/missions/resume-jd",
        json={
            "project_id": project_id,
            "resume_text": "Python SQL experience",
            "job_description": "Python SQL Kubernetes required",
        },
    )
    assert mission_resp.status_code == 201
    mission_id = mission_resp.json()["id"]

    # Create an approval request
    approval_response = client.post(
        f"/api/v1/missions/{mission_id}/approvals",
        params={"project_id": project_id},
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

    # Decide on the approval
    decision_response = client.patch(
        f"/api/v1/missions/{mission_id}/approvals/{approval['id']}",
        params={"project_id": project_id},
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

    # List approvals
    list_response = client.get(
        f"/api/v1/missions/{mission_id}/approvals",
        params={"project_id": project_id},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
