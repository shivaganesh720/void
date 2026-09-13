from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, DEFAULT_DEMO_USER_ID
from app.db.base import KnowledgeDocument, KnowledgeChunk, Memory, Project
from pydantic import BaseModel

router = APIRouter(tags=["knowledge"])

class MemoryCreate(BaseModel):
    key: str
    value: dict

@router.get("/api/v1/projects/{project_id}/knowledge")
def list_knowledge(project_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.project_id == project_id).all()
    return docs

@router.get("/api/v1/projects/{project_id}/memory")
def list_memory(project_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    memories = db.query(Memory).filter(Memory.project_id == project_id).all()
    return memories

@router.post("/api/v1/projects/{project_id}/memory")
def create_memory(project_id: UUID, payload: MemoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mem = Memory(
        project_id=project_id,
        user_id=current_user.id if hasattr(current_user, 'id') else DEFAULT_DEMO_USER_ID,
        key=payload.key,
        value_json=payload.value
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem
