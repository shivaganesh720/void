from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings
from app.db.base import Base, User
from app.db.session import database_health_check, get_engine_for_settings


def test_database_foundation_initializes_schema_and_round_trips_user(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'void_db.sqlite3'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    db = Session()
    user_id = uuid4()
    user = User(id=user_id, email="db-user@example.com", password_hash="test-hash")
    db.add(user)
    db.commit()

    row = db.execute(select(User).where(User.id == user_id)).scalar_one()
    assert row.email == "db-user@example.com"
    assert row.id == user_id

    db.close()
    engine.dispose()


def test_database_settings_expose_runtime_pool_and_health_configuration() -> None:
    settings = Settings(
        environment="test",
        database_url="sqlite:///:memory:",
        db_pool_size=10,
        db_max_overflow=20,
        db_pool_timeout=30,
        db_pool_recycle=1800,
        db_echo=True,
        runtime_db_path=".local/void.sqlite3",
    )

    assert settings.db_pool_size == 10
    assert settings.db_max_overflow == 20
    assert settings.db_pool_timeout == 30
    assert settings.db_pool_recycle == 1800
    assert settings.db_echo is True

    engine = get_engine_for_settings(settings)
    assert engine is not None
    assert database_health_check(engine) is True


def test_alembic_environment_targets_project_metadata() -> None:
    env_path = Path(__file__).resolve().parents[2] / "backend" / "alembic" / "env.py"
    content = env_path.read_text(encoding="utf-8")

    assert "target_metadata = Base.metadata" in content
    assert "database_url" in content or "Settings(" in content
