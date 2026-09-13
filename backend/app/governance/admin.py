from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    role: Role
    reason: str


class AdminAccessPolicy:
    """Simple role-based access policy for admin-only operations."""

    @staticmethod
    def _normalize_role(actor: str | Role | None) -> Role | None:
        if actor is None:
            return None
        if isinstance(actor, Role):
            return actor
        normalized = str(actor).strip().upper()
        if normalized in {"ADMIN", "ADMIN-USER"}:
            return Role.ADMIN
        if normalized == "AUDITOR":
            return Role.AUDITOR
        if normalized == "USER":
            return Role.USER
        return None

    def can_access(self, actor: str | Role | None, required_role: Role) -> bool:
        actor_role = self._normalize_role(actor)
        if actor_role is None:
            return False

        if required_role == Role.ADMIN:
            return actor_role == Role.ADMIN
        if required_role == Role.AUDITOR:
            return actor_role in {Role.ADMIN, Role.AUDITOR}
        return actor_role == required_role

    def evaluate(self, actor: str | Role | None, required_role: Role) -> AccessDecision:
        allowed = self.can_access(actor, required_role)
        return AccessDecision(
            allowed=allowed,
            role=required_role,
            reason="admin access granted" if allowed else "missing required role",
        )
