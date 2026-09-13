from datetime import UTC, datetime
from uuid import uuid4

from app.db.runtime import RuntimeStore


def test_runtime_store_round_trips_mission_payload(tmp_path) -> None:
    store = RuntimeStore(str(tmp_path / "void.sqlite3"))
    mission_id = uuid4()
    timestamp = datetime.now(UTC)
    payload = {
        "id": mission_id,
        "project_id": uuid4(),
        "intent": "test mission",
        "status": "COMPLETED",
        "task": {"id": uuid4(), "mission_id": mission_id, "name": "test", "status": "SUCCEEDED", "result": {"ok": True}, "error": None},
        "result": {"ok": True},
        "error": None,
        "execution_mode": "AUTO",
        "created_at": timestamp,
        "updated_at": timestamp,
        "completed_at": timestamp,
        "events": [],
    }

    store.save(payload)
    restored = store.load_all()

    assert len(restored) == 1
    assert restored[0]["id"] == str(mission_id)
    assert restored[0]["task"]["status"] == "SUCCEEDED"
    assert restored[0]["result"] == {"ok": True}
