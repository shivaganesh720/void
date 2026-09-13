import json
from pathlib import Path
from typing import Any


class MissionRepository:
    """Small durable repository layer for missions and task state."""

    def __init__(self, path: str = ".local/void-missions.sqlite3") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        import sqlite3

        if str(self.path) == ":memory:":
            connection = sqlite3.connect("file:mission_repo?mode=memory&cache=shared", uri=True)
        else:
            connection = sqlite3.connect(self.path.as_posix())
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS ix_missions_project ON missions(project_id)")

    def save_mission(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO missions (id, project_id, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    project_id=excluded.project_id,
                    payload=excluded.payload,
                    updated_at=excluded.updated_at
                """,
                (
                    str(payload["id"]),
                    str(payload["project_id"]),
                    json.dumps(payload, separators=(",", ":"), sort_keys=True),
                    payload.get("created_at", "2026-01-01T00:00:00+00:00"),
                    payload.get("updated_at", "2026-01-01T00:00:00+00:00"),
                ),
            )
        return payload

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM missions WHERE project_id = ? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def get_mission(self, mission_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM missions WHERE id = ?", (mission_id,)).fetchone()
        if row is None:
            return None
        return json.loads(row["payload"])
