from typing import Generator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.security import decode_token, hash_password
from app.models.base import ProjectMember, User
from app.db.session import create_session_factory
from app.repositories.projects import project_repo
from app.repositories.users import user_repo

settings = get_settings()

DEFAULT_DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000099")
DEFAULT_DEMO_USER_EMAIL = "demo@void.local"

SessionLocal = create_session_factory()


def _get_or_create_demo_user(db: Session) -> User:
    user = user_repo.get(db, DEFAULT_DEMO_USER_ID)
    if user:
        return user

    try:
        with db.begin_nested():
            user_repo.create(db, {
                "id": DEFAULT_DEMO_USER_ID,
                "email": DEFAULT_DEMO_USER_EMAIL,
                "password_hash": hash_password("demo-password"),
                "full_name": "Demo User",
                "role": "USER",
            })
    except IntegrityError:
        # Another request may have provisioned the fixed development identity.
        # The savepoint keeps this request's session usable after the race.
        pass

    return user_repo.get(db, DEFAULT_DEMO_USER_ID) or user_repo.get_by_id(db, DEFAULT_DEMO_USER_ID)


def _get_or_create_legacy_project(db: Session, project_id: UUID, owner_id: UUID):
    from app.models.base import Project

    project = project_repo.get(db, project_id)
    if project:
        return project
    try:
        with db.begin_nested():
            project = project_repo.create(db, {
                "id": project_id,
                "name": "Legacy Local Project",
                "owner_id": owner_id,
            })
            db.add(ProjectMember(project_id=project_id, user_id=owner_id, role="OWNER"))
            db.flush()
    except IntegrityError:
        project = project_repo.get(db, project_id)
    if not project:
        raise HTTPException(status_code=409, detail="PROJECT_PROVISIONING_CONFLICT")
    return project


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    # An explicitly supplied Bearer token represents the caller for this
    # request.  It must take precedence over a browser cookie: API clients
    # commonly share a cookie jar while exercising multiple identities, and
    # allowing the cookie to win can turn a request into a confused-deputy
    # authorization bug.
    token: str | None = None
    if authorization:
        scheme, _, token_from_header = authorization.partition(" ")
        if scheme.lower() == "bearer":
            token = token_from_header
    if not token:
        token = request.cookies.get("void_access_token")

    if not token:
        # Dev fallback – auto-provision demo user on first hit
        user = _get_or_create_demo_user(db)
        db.commit()
        return user

    decoded = decode_token(token, token_kind="access")
    if not decoded:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_INVALID_TOKEN")

    user_id, _email = decoded
    user = user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTH_USER_NOT_FOUND")

    return user


def require_project_access(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.base import Project, ProjectMember

    project = project_repo.get(db, project_id)
    if not project:
        if current_user.id == DEFAULT_DEMO_USER_ID:
            # Auto-provision legacy project for the demo user
            project = _get_or_create_legacy_project(db, project_id, current_user.id)
            db.commit()
            db.refresh(project)
            return project
        raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")

    # Demo user always has full access regardless of ownership (dev mode)
    if current_user.id == DEFAULT_DEMO_USER_ID:
        return project

    if project.owner_id != current_user.id and not project_repo.has_access(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="PROJECT_ACCESS_DENIED")

    return project


# Simple static RBAC policy mapping
ROLE_PERMISSIONS = {
    "OWNER": ["project:read", "project:update", "project:delete", "mission:read", "mission:create", "mission:execute", "mission:delete", "member:invite"],
    "ADMIN": ["project:read", "project:update", "mission:read", "mission:create", "mission:execute", "mission:delete", "member:invite"],
    "MEMBER": ["project:read", "mission:read", "mission:create", "mission:execute"],
    "VIEWER": ["project:read", "mission:read"],
}


class RequirePermission:
    def __init__(self, resource: str, action: str):
        self.permission = f"{resource}:{action}"

    def __call__(self, project_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        from app.models.base import Project, ProjectMember

        project = project_repo.get(db, project_id)

        if not project:
            if current_user.id == DEFAULT_DEMO_USER_ID:
                return require_project_access(project_id, current_user, db)
            raise HTTPException(status_code=404, detail="AUTH_RESOURCE_NOT_FOUND")

        # Demo user always has full access (dev mode)
        if current_user.id == DEFAULT_DEMO_USER_ID:
            return project

        role = "VIEWER"
        if project.owner_id == current_user.id:
            role = "OWNER"
        else:
            member = db.query(ProjectMember).filter_by(project_id=project_id, user_id=current_user.id).first()
            if not member:
                raise HTTPException(status_code=403, detail="AUTH_PERMISSION_DENIED")
            role = member.role

        if self.permission not in ROLE_PERMISSIONS.get(role, []):
            raise HTTPException(status_code=403, detail="AUTH_PERMISSION_DENIED")

        return project
