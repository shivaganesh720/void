from typing import Generic, TypeVar, Any
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, session: Session, id: UUID | str) -> ModelType | None:
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return None
        return session.get(self.model, id)

    def get_by_id(self, session: Session, id: UUID | str) -> ModelType:
        obj = self.get(session, id)
        if obj is None:
            raise NoResultFound(f"{self.model.__name__} not found")
        return obj

    def list(self, session: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(session.scalars(stmt).all())

    def create(self, session: Session, obj_in: dict[str, Any] | ModelType) -> ModelType:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        session.add(db_obj)
        session.flush()
        return db_obj

    def update(self, session: Session, *, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        session.flush()
        return db_obj

    def delete(self, session: Session, *, id: UUID | str) -> bool:
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return False
        stmt = delete(self.model).where(self.model.id == id)
        result = session.execute(stmt)
        return result.rowcount > 0
