"""Shared test fixtures providing a fresh in-memory SQLite database per test."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.api.deps import get_db
from app.main import app


@pytest.fixture(autouse=True)
def db_session():
    """Create a fresh in-memory SQLite DB for every test, wired into FastAPI DI."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def _override():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override
    test_session = TestingSessionLocal()
    yield test_session
    test_session.close()
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def client():
    return TestClient(app)
