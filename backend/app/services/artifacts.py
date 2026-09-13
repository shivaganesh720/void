from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4


class ArtifactRetentionService:
    """Minimal durable artifact registry with retention checks."""

    def __init__(self, path: str = ".local/void-artifacts.sqlite3") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        import sqlite3

        if str(self.path) == ":memory:":
            connection = sqlite3.connect("file:artifact_service?mode=memory&cache=shared", uri=True)
        else:
            connection = sqlite3.connect(self.path.as_posix())
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    mission_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
                """
            )

    def register_artifact(
        self,
        *,
        project_id: str,
        mission_id: str,
        artifact_type: str,
        content: str,
        owner_id: str,
        age_days: int = 0,
    ) -> dict[str, Any]:
        artifact_id = str(uuid4())
        created_at = datetime.now(UTC) - timedelta(days=age_days)
        expires_at = created_at + timedelta(days=30)
        payload = {
            "id": artifact_id,
            "project_id": project_id,
            "mission_id": mission_id,
            "artifact_type": artifact_type,
            "owner_id": owner_id,
            "status": "CREATED",
            "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "content": content,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO artifacts (id, project_id, mission_id, artifact_type, owner_id, status, content_hash, content, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    payload["id"],
                    payload["project_id"],
                    payload["mission_id"],
                    payload["artifact_type"],
                    payload["owner_id"],
                    payload["status"],
                    payload["content_hash"],
                    payload["content"],
                    payload["created_at"],
                    payload["expires_at"],
                ),
            )
        return payload

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
        if row is None:
            return None
        return dict(row)

    def should_expire(self, artifact_id: str) -> bool:
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False
        expires_at = datetime.fromisoformat(artifact["expires_at"])
        return datetime.now(UTC) > expires_at

    def list_expired(self) -> list[dict[str, Any]]:
        now = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM artifacts WHERE expires_at < ? ORDER BY created_at DESC",
                (now,),
            ).fetchall()
        return [dict(row) for row in rows]
