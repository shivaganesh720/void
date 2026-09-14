from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, session: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email.casefold())
        return session.execute(stmt).scalar_one_or_none()


user_repo = UserRepository()
