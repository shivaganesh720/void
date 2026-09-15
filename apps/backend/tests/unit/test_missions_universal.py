import hashlib
from pathlib import Path
from uuid import UUID, uuid4

import app.middleware as middleware
from app.models.base import Artifact, AuditEvent, Evidence, LifecycleEvent, MissionOutput, PolicyDecisionRecord
from fastapi.testclient import TestClient


def test_create_universal_mission_persists_governed_execution(client: TestClient, db_session, monkeypatch):
    project_id = str(uuid4())

    monkeypatch.setattr(middleware, "SessionLocal", lambda: db_session)
    response = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": project_id,
            "prompt": "Draft an executive project update",
        }
    )
    assert response.status_code == 201
    data = response.json()
    mission_id = data["id"]
    task_id = data["task"]["id"]
    assert data["status"] == "COMPLETED"
    assert data["task"]["status"] == "SUCCEEDED"
    assert data["result"]["validation"]["status"] == "PASSED"

    mission = client.get(f"/api/v1/missions/{mission_id}?project_id={project_id}").json()
    artifact = db_session.query(Artifact).filter(Artifact.mission_id == UUID(mission_id)).one()
    artifact_path = Path(artifact.storage_location)
    assert artifact_path.exists()
    assert artifact.content_hash == hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    assert db_session.query(PolicyDecisionRecord).filter(PolicyDecisionRecord.mission_id == UUID(mission_id)).one().decision == "ALLOW"
    assert db_session.query(MissionOutput).filter(MissionOutput.mission_id == UUID(mission_id)).one().content_json == mission["result"]
    evidence = db_session.query(Evidence).filter(Evidence.mission_id == UUID(mission_id)).one()
    assert str(evidence.task_id) == task_id
    events = db_session.query(LifecycleEvent).filter(LifecycleEvent.mission_id == UUID(mission_id)).order_by(LifecycleEvent.created_at).all()
    assert [event.event_type for event in events] == [
        "MISSION_REQUESTED", "INTENT_NORMALIZED", "BLUEPRINT_CREATED", "MISSION_READY", "EXECUTION_STARTED", "MISSION_COMPLETED",
    ]
    audit = db_session.query(AuditEvent).filter(AuditEvent.project_id == UUID(project_id)).one()
    assert audit.event_type == "POST /api/v1/missions/universal"


def test_create_universal_mission_routing(client: TestClient, db_session):
    project_id = str(uuid4())

    response = client.post(
        "/api/v1/missions/universal",
        json={"project_id": project_id, "prompt": "Research the latest framework"},
    )
    assert response.status_code == 201
    data = response.json()
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

    response = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": project_id,
            "prompt": "Analyze this csv data",
        }
    )
    assert response.status_code == 201
    assert response.json()["status"] == "WAITING_FOR_INPUT"

    other_project = str(uuid4())
    response = client.post(
        "/api/v1/missions/universal",
        json={
            "project_id": other_project,
            "prompt": "Unknown task",
        }
    )
    assert response.status_code == 201
    assert response.json()["status"] == "COMPLETED"
    assert response.json()["result"]["agent"]["name"] == "Manager / Supervisor Agent"
