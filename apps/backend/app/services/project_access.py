from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectAccessContext:
    user_id: str
    role: str = "USER"
    project_owner_id: str | None = None
    members: tuple[str, ...] = ()


class ProjectAccessService:
    """Central policy layer for project membership and ownership checks."""

    def __init__(self) -> None:
        self._projects: dict[str, ProjectAccessContext] = {}

    def register_project(self, *, project_id: str, owner_id: str, members: list[str] | None = None) -> None:
        self._projects[project_id] = ProjectAccessContext(
            user_id=owner_id,
            role="OWNER",
            project_owner_id=owner_id,
            members=tuple(set([owner_id, *(members or [])])),
        )

    def user_has_project_access(self, *, user_id: str, project_id: str) -> bool:
        context = self._projects.get(project_id)
        if context is None:
            return False
        return user_id in context.members or user_id == context.project_owner_id

    def require_member(self, *, user_id: str, project_id: str) -> ProjectAccessContext:
        if not self.user_has_project_access(user_id=user_id, project_id=project_id):
            raise PermissionError(f"User '{user_id}' does not have access to project '{project_id}'.")
        return self._projects[project_id]

    def require_owner(self, *, user_id: str, project_id: str) -> ProjectAccessContext:
        context = self.require_member(user_id=user_id, project_id=project_id)
        if context.project_owner_id != user_id:
            raise PermissionError(f"User '{user_id}' is not the owner of project '{project_id}'.")
        return context

    def can_administer(self, *, user_id: str, project_id: str) -> bool:
        context = self._projects.get(project_id)
        if context is None:
            return False
        return user_id == context.project_owner_id or context.role == "ADMIN"

    def list_projects_for_user(self, *, user_id: str) -> list[str]:
        return [project_id for project_id, context in self._projects.items() if self.user_has_project_access(user_id=user_id, project_id=project_id)]
