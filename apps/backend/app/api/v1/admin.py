from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.schemas import AdminOverviewResponse, AdminUserResponse
from app.models.base import User, Project, Mission
from app.policies.permissions import AdminAccessPolicy, Role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not AdminAccessPolicy().can_access(current_user.role, Role.ADMIN):
        raise HTTPException(status_code=403, detail="ADMIN_REQUIRED")

    users = db.query(User).all()
    admin_count = sum(1 for candidate in users if AdminAccessPolicy().can_access(candidate.role, Role.ADMIN))
    auditor_count = sum(1 for candidate in users if AdminAccessPolicy().can_access(candidate.role, Role.AUDITOR))
    
    project_count = db.query(Project).count()
    mission_count = db.query(Mission).count()
    
    return {
        "user_count": len(users),
        "admin_count": admin_count,
        "auditor_count": auditor_count,
        "project_count": project_count,
        "mission_count": mission_count,
    }


@router.get("/users", response_model=list[AdminUserResponse])
def admin_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not AdminAccessPolicy().can_access(current_user.role, Role.ADMIN):
        raise HTTPException(status_code=403, detail="ADMIN_REQUIRED")

    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "full_name": u.full_name,
            "created_at": u.created_at,
            "status": "active"
        }
        for u in users
    ]
