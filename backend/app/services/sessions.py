from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4


class SessionStore:
    """Compact session and refresh-token store with rotation and revocation."""

    def __init__(self, path: str = ".local/void-sessions.sqlite3") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        import sqlite3

        if str(self.path) == ":memory:":
            connection = sqlite3.connect("file:session_service?mode=memory&cache=shared", uri=True)
        else:
            connection = sqlite3.connect(self.path.as_posix())
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    access_expires_at TEXT NOT NULL,
                    refresh_expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def _encode_token(self, user_id: str, email: str, *, token_kind: str, ttl: timedelta) -> str:
        secret = secrets.token_urlsafe(32)
        payload = {
            "sub": user_id,
            "email": email,
            "kind": token_kind,
            "exp": (datetime.now(UTC) + ttl).timestamp(),
            "nonce": secret,
        }
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return f"{hashlib.sha256(body).hexdigest()}.{signature}"

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def create_session(self, *, user_id: str, email: str, role: str) -> dict[str, Any]:
        session_id = str(uuid4())
        access_token = self._encode_token(user_id, email, token_kind="access", ttl=timedelta(hours=1))
        refresh_token = self._encode_token(user_id, email, token_kind="refresh", ttl=timedelta(days=30))
        created_at = datetime.now(UTC)
        record = {
            "id": session_id,
            "user_id": user_id,
            "email": email,
            "role": role,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_expires_at": (created_at + timedelta(hours=1)).isoformat(),
            "refresh_expires_at": (created_at + timedelta(days=30)).isoformat(),
            "created_at": created_at.isoformat(),
            "revoked": 0,
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO sessions (id, user_id, email, role, access_token, refresh_token, access_expires_at, refresh_expires_at, created_at, revoked) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record["id"],
                    record["user_id"],
                    record["email"],
                    record["role"],
                    record["access_token"],
                    record["refresh_token"],
                    record["access_expires_at"],
                    record["refresh_expires_at"],
                    record["created_at"],
                    record["revoked"],
                ),
            )
        return record

    def validate_session(self, token: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE (access_token = ? OR refresh_token = ?) AND revoked = 0",
                (token, token),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def rotate_session(self, refresh_token: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE refresh_token = ? AND revoked = 0",
                (refresh_token,),
            ).fetchone()
        if row is None:
            raise PermissionError("INVALID_REFRESH_TOKEN")

        user_id = row["user_id"]
        email = row["email"]
        role = row["role"]
        new_access = self._encode_token(user_id, email, token_kind="access", ttl=timedelta(hours=1))
        new_refresh = self._encode_token(user_id, email, token_kind="refresh", ttl=timedelta(days=30))
        revoked_at = datetime.now(UTC)

        with self._connect() as connection:
            connection.execute(
                "UPDATE sessions SET access_token = ?, refresh_token = ?, access_expires_at = ?, refresh_expires_at = ?, revoked = 1 WHERE refresh_token = ?",
                (
                    new_access,
                    new_refresh,
                    (revoked_at + timedelta(hours=1)).isoformat(),
                    (revoked_at + timedelta(days=30)).isoformat(),
                    refresh_token,
                ),
            )
            connection.execute(
                "INSERT INTO sessions (id, user_id, email, role, access_token, refresh_token, access_expires_at, refresh_expires_at, created_at, revoked) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid4()),
                    user_id,
                    email,
                    role,
                    new_access,
                    new_refresh,
                    (revoked_at + timedelta(hours=1)).isoformat(),
                    (revoked_at + timedelta(days=30)).isoformat(),
                    revoked_at.isoformat(),
                    0,
                ),
            )

        return {"access_token": new_access, "refresh_token": new_refresh}

    def revoke_user_sessions(self, user_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute("UPDATE sessions SET revoked = 1 WHERE user_id = ?", (user_id,))
        return cursor.rowcount
