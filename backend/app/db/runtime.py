from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID


class RuntimeStore:
    """Small local persistence boundary for the current development slice."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path.as_posix() if str(self.path) != ":memory:" else ":memory:")
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
            connection.execute("CREATE INDEX IF NOT EXISTS ix_missions_project_id ON missions(project_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS ix_missions_updated_at ON missions(updated_at)")

    def save(self, payload: dict[str, Any]) -> None:
        mission_id = str(payload["id"])
        project_id = str(payload["project_id"])
        serialized = json.dumps(payload, default=json_default, separators=(",", ":"), sort_keys=True)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO missions (id, project_id, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    project_id=excluded.project_id,
                    payload=excluded.payload,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (mission_id, project_id, serialized, json_default(payload["created_at"]), json_default(payload["updated_at"])),
            )

    def load_all(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT payload FROM missions ORDER BY updated_at DESC").fetchall()
        return [json.loads(row["payload"]) for row in rows]


def json_default(value: Any) -> str:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported runtime value: {type(value).__name__}")
