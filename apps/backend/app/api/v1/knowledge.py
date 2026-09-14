from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.base import KnowledgeDocument

router = APIRouter(tags=["knowledge"])


@router.get("/api/v1/projects/{project_id}/knowledge")
def list_knowledge(project_id: UUID, db: Session = Depends(get_db)):
    docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.project_id == project_id).all()
    return docs

@router.post("/api/v1/projects/{project_id}/knowledge/ingest")
def ingest_knowledge(project_id: UUID, source: str, title: str, db: Session = Depends(get_db)):
    from app.services.knowledge import IngestionService
    svc = IngestionService(db)
    return svc.ingest_document(project_id, source, title)
