from uuid import uuid4

from sqlalchemy import select

from app.db.base import Base, User
from app.db.session import SessionLocal, initialize_database


def test_database_foundation_initializes_schema_and_round_trips_user(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'void_db.sqlite3'}"
    initialize_database(database_url)

    db = SessionLocal(database_url)
    user_id = uuid4()
    user = User(id=user_id, email="db-user@example.com")
    db.add(user)
    db.commit()

    row = db.execute(select(User).where(User.id == user_id)).scalar_one()
    assert row.email == "db-user@example.com"
    assert row.id == user_id

    db.close()

    Base.metadata.clear()
