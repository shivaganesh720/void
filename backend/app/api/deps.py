from typing import Generator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_token, hash_password
from app.db.base import User
from app.db.session import create_session_factory
from app.repositories.projects import project_repo
from app.repositories.users import user_repo

settings = get_settings()

DEFAULT_DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000099")
DEFAULT_DEMO_USER_EMAIL = "demo@void.local"

SessionLocal = create_session_factory()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        # Dev fallback – auto-provision demo user on first hit
        user = user_repo.get(db, DEFAULT_DEMO_USER_ID)
        if not user:
            user = user_repo.create(db, {
                "id": DEFAULT_DEMO_USER_ID,
                "email": DEFAULT_DEMO_USER_EMAIL,
                "password_hash": hash_password("demo-password"),
                "full_name": "Demo User",
                "role": "USER",
            })
            db.commit()
        return user

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")

    decoded = decode_token(token, token_kind="access")
    if not decoded:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id, _email = decoded
    user = user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_project_access(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.db.base import Project, ProjectMember

    project = project_repo.get(db, project_id)
    if not project:
        # Auto-provision legacy project for the demo user
        if current_user.id == DEFAULT_DEMO_USER_ID:
            project = project_repo.create(db, {
                "id": project_id,
                "name": "Legacy Local Project",
                "owner_id": current_user.id,
            })
            member = ProjectMember(project_id=project.id, user_id=current_user.id, role="OWNER")
            db.add(member)
            db.commit()
            db.refresh(project)
            return project
        raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")

    if project.owner_id != current_user.id and not project_repo.has_access(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="PROJECT_ACCESS_DENIED")

    return project
