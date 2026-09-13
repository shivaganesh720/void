from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base


DEFAULT_DATABASE_URL = "sqlite:///./.local/void.sqlite3"


def create_session_factory(database_url: str = DEFAULT_DATABASE_URL) -> sessionmaker[Session]:
    engine = create_engine(database_url, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def initialize_database(database_url: str = DEFAULT_DATABASE_URL) -> None:
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(bind=engine)


def SessionLocal(database_url: str = DEFAULT_DATABASE_URL) -> Session:
    return create_session_factory(database_url)()
