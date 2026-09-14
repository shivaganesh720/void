from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4


class AuthService:
    """Durable auth and project membership service."""

    def __init__(self, path: str = ".local/void-auth.sqlite3") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        import sqlite3

        if str(self.path) == ":memory:":
            connection = sqlite3.connect("file:auth_service?mode=memory&cache=shared", uri=True)
        else:
            connection = sqlite3.connect(self.path.as_posix())
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    onboarding_completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    members TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
        return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            algorithm, rounds_text, salt_hex, digest_hex = stored_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            rounds = int(rounds_text)
            expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), rounds).hex()
            return hmac.compare_digest(expected, digest_hex)
        except (TypeError, ValueError):
            return False

    def register_user(self, full_name: str, email: str, password: str) -> dict:
        if not email or "@" not in email:
            raise ValueError("INVALID_EMAIL")
        if len(password) < 8:
            raise ValueError("WEAK_PASSWORD")

        user_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        payload = {
            "id": user_id,
            "email": email.casefold(),
            "password_hash": self._hash_password(password),
            "full_name": full_name.strip() or "User",
            "role": "USER",
            "onboarding_completed": False,
            "created_at": now,
        }

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO users (id, email, password_hash, full_name, role, onboarding_completed, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    payload["id"],
                    payload["email"],
                    payload["password_hash"],
                    payload["full_name"],
                    payload["role"],
                    int(payload["onboarding_completed"]),
                    payload["created_at"],
                ),
            )
        return payload

    def authenticate_user(self, email: str, password: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.casefold(),),
            ).fetchone()
        if row is None:
            return None
        if not self._verify_password(password, row["password_hash"]):
            return None
        return {
            "id": row["id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "role": row["role"],
            "onboarding_completed": bool(row["onboarding_completed"]),
            "created_at": row["created_at"],
        }

    def create_project(self, owner_id: str, name: str) -> dict:
        if not name.strip():
            raise ValueError("INVALID_PROJECT_NAME")
        project_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        payload = {
            "id": project_id,
            "owner_id": owner_id,
            "name": name.strip(),
            "members": [owner_id],
            "created_at": now,
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO projects (id, owner_id, name, members, created_at) VALUES (?, ?, ?, ?, ?)",
                (payload["id"], payload["owner_id"], payload["name"], json.dumps(payload["members"]), payload["created_at"]),
            )
        return payload

    def user_has_project_access(self, user_id: str, project_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT members FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            return False
        members = json.loads(row["members"])
        return user_id in members
