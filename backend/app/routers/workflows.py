from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.base import Workflow, WorkflowVersion

router = APIRouter(tags=["workflows"])

@router.get("/api/v1/workflows")
def list_workflows(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Workflow).all()

@router.get("/api/v1/workflows/{workflow_id}")
def get_workflow(workflow_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    w = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not w:
        raise HTTPException(404, "WORKFLOW_NOT_FOUND")
    return w

@router.get("/api/v1/workflows/{workflow_id}/versions")
def get_workflow_versions(workflow_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    versions = db.query(WorkflowVersion).filter(WorkflowVersion.workflow_id == workflow_id).all()
    return versions
