"""Lightweight mission repository for the MissionService layer.

This provides a simple dict-based persistence backed by SQLite for the
service-layer tests. The *API-layer* persistence now uses the full
SQLAlchemy ORM (see app.db.base / app.routers.missions).
"""
from __future__ import annotations

import json
import sqlite3
from typing import Any
from uuid import UUID


class _JsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


class MissionRepository:
    """Dict-in / dict-out mission store backed by a single SQLite table."""

    def __init__(self, path: str = ".local/void-missions.sqlite3") -> None:
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS missions ("
            "  id TEXT PRIMARY KEY,"
            "  project_id TEXT NOT NULL,"
            "  payload TEXT NOT NULL"
            ")"
        )
        self._conn.commit()

    # --- write -----------------------------------------------------------
    def save_mission(self, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO missions (id, project_id, payload) VALUES (?, ?, ?)",
            (str(payload["id"]), str(payload.get("project_id", "")), json.dumps(payload, cls=_JsonEncoder)),
        )
        self._conn.commit()

    # --- read ------------------------------------------------------------
    def get_mission(self, mission_id: str) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT payload FROM missions WHERE id = ?", (str(mission_id),)).fetchone()
        return json.loads(row[0]) if row else None

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT payload FROM missions WHERE project_id = ?", (str(project_id),)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def list_all(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT payload FROM missions").fetchall()
        return [json.loads(r[0]) for r in rows]
