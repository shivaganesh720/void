import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.config import get_settings

settings = get_settings()
SECRET_KEY = settings.database_url.encode() if settings.database_url else b"void-local-dev-secret"

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, rounds_text, salt_hex, digest_hex = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return hmac.compare_digest(stored_hash, hash_password(password))
        rounds = int(rounds_text)
        expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), rounds).hex()
        return hmac.compare_digest(expected, digest_hex)
    except (TypeError, ValueError):
        return False


def encode_token(user_id: UUID, email: str, token_kind: str = "access", ttl: timedelta | None = None) -> str:
    ttl = ttl or (timedelta(days=7) if token_kind == "refresh" else timedelta(hours=1))
    payload = {"sub": str(user_id), "email": email, "kind": token_kind, "exp": (datetime.now(UTC) + ttl).timestamp()}
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii").rstrip("=")
    signature = hmac.new(SECRET_KEY, body.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def decode_token(token: str, token_kind: str | None = None) -> tuple[UUID, str] | None:
    try:
        signing_input, signature = token.split(".", 1)
    except ValueError:
        return None
    expected = hmac.new(SECRET_KEY, signing_input.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(signing_input + "=" * (-len(signing_input) % 4)).decode("utf-8"))
    except Exception:
        return None
    exp = float(payload.get("exp", 0))
    if exp < datetime.now(UTC).timestamp():
        return None
    if token_kind is not None and payload.get("kind") != token_kind:
        return None
    try:
        return UUID(payload["sub"]), str(payload.get("email"))
    except (TypeError, ValueError):
        return None


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
