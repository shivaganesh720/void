import pytest
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from app.models.base import Project, Mission
from app.api.deps import get_db
from app.main import app

def test_transaction_rollback_on_integrity_error(db_session):
    db = next(app.dependency_overrides[get_db]())
    try:
        project_id = uuid4()
        owner_id = uuid4()
        from app.models.base import User
        valid_user = User(id=owner_id, email="test@test.com", password_hash="hash", role="USER")
        db.add(valid_user)
        db.commit()
        
        # Intentionally violate NOT NULL constraint (name missing)
        invalid_project = Project(id=project_id, owner_id=owner_id)
        
        db.add(invalid_project)
        
        with pytest.raises(IntegrityError):
            db.commit()
        
        db.rollback()
        
        # Ensure the session is still usable after rollback
        valid_project = Project(id=project_id, name="Valid Project", owner_id=owner_id)
        db.add(valid_project)
        db.commit()
        
        assert db.query(Project).filter_by(id=project_id).first().name == "Valid Project"
    finally:
        db.close()

def test_foreign_key_constraint_prevents_orphans(db_session):
    db = next(app.dependency_overrides[get_db]())
    try:
        invalid_mission = Mission(
            id=uuid4(),
            project_id=uuid4(), # Project doesn't exist
            intent="Test",
            status="PENDING",
            execution_mode="AUTO"
        )
        
        db.add(invalid_mission)
        with pytest.raises(IntegrityError):
            db.commit()
        
        db.rollback()
    finally:
        db.close()
