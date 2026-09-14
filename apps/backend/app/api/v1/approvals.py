from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db, get_current_user
from app.models.enums import ApprovalStatus
from app.schemas import ApprovalRequest, ApprovalDecisionUpdate, ApprovalResponse
from app.models.base import User, Mission, Approval
from app.api.v1.missions import _ensure_project_access

router = APIRouter(tags=["approvals"])


@router.post("/api/v1/missions/{mission_id}/approvals", response_model=ApprovalResponse, status_code=201)
def create_approval(
    mission_id: UUID,
    payload: ApprovalRequest,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    _ensure_project_access(db, project_id, current_user)

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.project_id == project_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="MISSION_NOT_FOUND")

    approval = Approval(
        mission_id=mission_id,
        requested_action=payload.requested_action,
        risk_reason=payload.risk_reason,
        required_by_policy=payload.required_by_policy,
        reviewer_id=payload.reviewer_id,
        status=ApprovalStatus.PENDING.value,
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)

    return {
        "id": approval.id,
        "mission_id": approval.mission_id,
        "task_id": None,
        "requested_action": approval.requested_action,
        "risk_reason": approval.risk_reason,
        "required_by_policy": approval.required_by_policy,
        "status": ApprovalStatus(approval.status),
        "requested_at": approval.created_at,
        "reviewed_at": approval.reviewed_at,
        "reviewer_id": approval.reviewer_id,
        "reviewer_comment": approval.reviewer_comment,
        "expiration": approval.expiration,
        "metadata": approval.metadata_json or {},
    }


@router.patch("/api/v1/missions/{mission_id}/approvals/{approval_id}", response_model=ApprovalResponse)
def decide_approval(
    mission_id: UUID,
    approval_id: UUID,
    payload: ApprovalDecisionUpdate,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    _ensure_project_access(db, project_id, current_user)

    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.mission_id == mission_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="APPROVAL_NOT_FOUND")

    approval.status = payload.decision.value
    approval.reviewer_id = payload.reviewer_id
    approval.reviewer_comment = payload.reviewer_comment
    approval.reviewed_at = datetime.now(UTC)
    db.commit()
    db.refresh(approval)

    return {
        "id": approval.id,
        "mission_id": approval.mission_id,
        "task_id": approval.task_id,
        "requested_action": approval.requested_action,
        "risk_reason": approval.risk_reason,
        "required_by_policy": approval.required_by_policy,
        "status": ApprovalStatus(approval.status),
        "requested_at": approval.created_at,
        "reviewed_at": approval.reviewed_at,
        "reviewer_id": approval.reviewer_id,
        "reviewer_comment": approval.reviewer_comment,
        "expiration": approval.expiration,
        "metadata": approval.metadata_json or {},
    }


@router.get("/api/v1/missions/{mission_id}/approvals", response_model=list[ApprovalResponse])
def list_approvals(
    mission_id: UUID,
    project_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    _ensure_project_access(db, project_id, current_user)

    approvals = db.query(Approval).filter(Approval.mission_id == mission_id).all()
    return [
        {
            "id": a.id,
            "mission_id": a.mission_id,
            "task_id": a.task_id,
            "requested_action": a.requested_action,
            "risk_reason": a.risk_reason,
            "required_by_policy": a.required_by_policy,
            "status": ApprovalStatus(a.status),
            "requested_at": a.created_at,
            "reviewed_at": a.reviewed_at,
            "reviewer_id": a.reviewer_id,
            "reviewer_comment": a.reviewer_comment,
            "expiration": a.expiration,
            "metadata": a.metadata_json or {},
        }
        for a in approvals
    ]
