from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class AuditLogService:
    """Durable audit log for administrative and mission actions."""

    def __init__(self, path: str = ".local/void-audit.sqlite3") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        if str(self.path) == ":memory:":
            connection = sqlite3.connect("file:audit_service?mode=memory&cache=shared", uri=True)
        else:
            connection = sqlite3.connect(self.path.as_posix())
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    actor_id TEXT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def record_event(self, *, project_id: str, actor_id: str | None, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event_id = str(uuid4())
        timestamp = datetime.now(UTC).isoformat()
        row = {
            "id": event_id,
            "project_id": project_id,
            "actor_id": actor_id,
            "event_type": event_type,
            "payload": json.dumps(payload, separators=(",", ":"), sort_keys=True),
            "created_at": timestamp,
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO audit_events (id, project_id, actor_id, event_type, payload, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (row["id"], row["project_id"], row["actor_id"], row["event_type"], row["payload"], row["created_at"]),
            )
        return row

    def filter_events(self, *, project_id: str | None = None, actor_id: str | None = None, event_type: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM audit_events WHERE 1=1"
        params: list[str] = []
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if actor_id is not None:
            query += " AND actor_id = ?"
            params.append(actor_id)
        if event_type is not None:
            query += " AND event_type = ?"
            params.append(event_type)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]
