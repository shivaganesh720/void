from app.policies.permissions import AdminAccessPolicy, Role
from app.services.sessions import SessionStore


def test_session_store_rotates_and_revokes_tokens() -> None:
    store = SessionStore(path=":memory:")
    session = store.create_session(user_id="user-42", email="admin@example.com", role="ADMIN")
    assert store.validate_session(session["access_token"]) is not None

    rotated = store.rotate_session(session["refresh_token"])
    assert rotated["access_token"] != session["access_token"]
    assert rotated["refresh_token"] != session["refresh_token"]

    assert store.validate_session(session["refresh_token"]) is None
    assert store.revoke_user_sessions("user-42") >= 1


def test_admin_policy_enforces_admin_access() -> None:
    policy = AdminAccessPolicy()
    assert policy.can_access("admin-user", Role.ADMIN) is True
    assert policy.can_access("regular-user", Role.ADMIN) is False
    assert policy.evaluate("admin-user", Role.ADMIN).allowed is True
