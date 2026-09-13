from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_project_access
from app.contracts.schemas import ProjectCreateRequest, ProjectResponse
from app.db.base import User, ProjectMember
from app.repositories.projects import project_repo

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(payload: ProjectCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = project_repo.create(db, {
        "name": payload.name,
        "owner_id": current_user.id
    })
    
    # Add owner as project member
    member = ProjectMember(project_id=project.id, user_id=current_user.id, role="OWNER")
    db.add(member)
    db.commit()
    db.refresh(project)
    
    return {
        "id": project.id,
        "name": project.name,
        "owner_id": project.owner_id,
        "members": [current_user.id],
        "created_at": project.created_at
    }


@router.get("", response_model=list[ProjectResponse])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = project_repo.get_for_user(db, current_user.id)
    result = []
    for p in projects:
        # Find members
        members = [m.user_id for m in db.query(ProjectMember).filter(ProjectMember.project_id == p.id).all()]
        result.append({
            "id": p.id,
            "name": p.name,
            "owner_id": p.owner_id,
            "members": members,
            "created_at": p.created_at
        })
    return result
