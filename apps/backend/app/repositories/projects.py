from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Project, ProjectMember
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    def get_by_owner(self, session: Session, owner_id: UUID | str) -> list[Project]:
        if isinstance(owner_id, str):
            owner_id = UUID(owner_id)
        stmt = select(Project).where(Project.owner_id == owner_id)
        return list(session.scalars(stmt).all())

    def get_for_user(self, session: Session, user_id: UUID | str) -> list[Project]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            select(Project)
            .join(ProjectMember, Project.id == ProjectMember.project_id)
            .where(ProjectMember.user_id == user_id)
        )
        return list(session.scalars(stmt).all())

    def has_access(self, session: Session, project_id: UUID | str, user_id: UUID | str) -> bool:
        if isinstance(project_id, str):
            project_id = UUID(project_id)
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
        return session.execute(stmt).scalar_one_or_none() is not None


project_repo = ProjectRepository()
