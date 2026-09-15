import base64

from app.api.deps import DEFAULT_DEMO_USER_ID
from app.models.base import Project, User


def _create_demo_user(db):
    user = db.query(User).filter(User.id == DEFAULT_DEMO_USER_ID).first()
    if not user:
        db.add(
            User(
                id=DEFAULT_DEMO_USER_ID,
                email="demo@void.local",
                password_hash="demo-password",
                full_name="Demo User",
                role="USER",
            )
        )
        db.commit()


def test_voice_command_creates_real_mission(client, db_session):
    _create_demo_user(db_session)
    project = Project(name="Voice Project", owner_id=DEFAULT_DEMO_USER_ID)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    response = client.post(
        "/api/v1/companion/voice/command",
        json={
            "project_id": str(project.id),
            "prompt": "Analyze the sales CSV and summarize trends",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["project_id"] == str(project.id)
    assert data["intent"] == "Analyze the sales CSV and summarize trends"
    assert data["status"] in {"READY", "WAITING_FOR_APPROVAL", "WAITING_FOR_INPUT", "PLANNED", "RUNNING", "COMPLETED"}


def test_voice_transcribe_accepts_base64_audio(client, db_session):
    _create_demo_user(db_session)
    project = Project(name="Audio Project", owner_id=DEFAULT_DEMO_USER_ID)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    audio_payload = base64.b64encode(b"VOICE:Summarize my project status").decode("utf-8")
    response = client.post(
        "/api/v1/companion/voice/command",
        json={
            "project_id": str(project.id),
            "audio_base64": audio_payload,
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["intent"] == "Summarize my project status"
