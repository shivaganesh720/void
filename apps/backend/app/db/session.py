from __future__ import annotations

from typing import Any
from pathlib import Path

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings
from app.models.base import Base


DEFAULT_DATABASE_URL = "sqlite:///./.local/void.sqlite3"


def _ensure_sqlite_parent(database_url: str) -> None:
    """Create the parent directory for file-backed SQLite databases."""
    database = make_url(database_url).database
    if not database or database == ":memory:":
        return
    Path(database).expanduser().parent.mkdir(parents=True, exist_ok=True)


def _build_engine_kwargs(database_url: str, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    engine_kwargs: dict[str, Any] = {"future": True, "echo": bool(settings.db_echo)}

    if database_url.startswith("sqlite"):
        _ensure_sqlite_parent(database_url)
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        if make_url(database_url).database in {None, ":memory:"}:
            # In-memory databases need one shared connection so their schema
            # survives across sessions. File-backed SQLite must use the
            # default pool so concurrent requests do not share one cursor.
            engine_kwargs["poolclass"] = StaticPool
        return engine_kwargs

    engine_kwargs.update(
        {
            "pool_size": int(settings.db_pool_size),
            "max_overflow": int(settings.db_max_overflow),
            "pool_timeout": int(settings.db_pool_timeout),
            "pool_recycle": int(settings.db_pool_recycle),
        }
    )
    return engine_kwargs


def get_engine_for_settings(settings: Settings | None = None) -> Engine:
    settings = settings or get_settings()
    db_url = settings.database_url or DEFAULT_DATABASE_URL
    return create_engine(db_url, **_build_engine_kwargs(db_url, settings))


def create_session_factory(database_url: str | None = None, settings: Settings | None = None) -> sessionmaker[Session]:
    settings = settings or get_settings()
    actual_url = database_url or settings.database_url
    engine = create_engine(actual_url, **_build_engine_kwargs(actual_url, settings))
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def initialize_database(database_url: str | None = None, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    actual_url = database_url or settings.database_url
    
    # Apply the overridden DB url to settings if needed for engine builder
    custom_settings = Settings(**{**settings.model_dump(), "database_url": actual_url})
    engine = get_engine_for_settings(custom_settings)
    
    Base.metadata.create_all(bind=engine)
    engine.dispose()


def database_health_check(engine: Engine | str) -> bool:
    target = engine if isinstance(engine, Engine) else create_engine(engine, **_build_engine_kwargs(engine, get_settings()))
    try:
        with target.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        if not isinstance(engine, Engine):
            target.dispose()


def SessionLocal(database_url: str = DEFAULT_DATABASE_URL) -> Session:
    return create_session_factory(database_url)()
