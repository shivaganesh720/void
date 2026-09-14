import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import Memory
from app.api.deps import get_db

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.post("/")
def create_memory(key: str, value: str, project_id: str | None = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Create a new memory record."""
    pid = uuid.UUID(project_id) if project_id else None
    mem = Memory(key=key, value=value, project_id=pid, approved=True)
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return {"id": mem.id, "key": mem.key, "value": mem.value, "project_id": mem.project_id}


@router.get("/")
def list_memory(project_id: str | None = None, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """List memory records."""
    query = db.query(Memory)
    if project_id:
        query = query.filter(Memory.project_id == uuid.UUID(project_id))
    memories = query.all()
    return [{"id": m.id, "key": m.key, "value": m.value, "approved": m.approved} for m in memories]


@router.delete("/{memory_id}")
def delete_memory(memory_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete a memory record."""
    mem = db.query(Memory).filter(Memory.id == uuid.UUID(memory_id)).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(mem)
    db.commit()
    return {"status": "deleted"}
