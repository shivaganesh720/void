from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.enums import ApprovalStatus, ExecutionMode, MissionStatus, PolicyDecision, RiskLevel


class HealthResponse(BaseModel):
    status: str
    service: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    retryable: bool = False
    correlation_id: str | None = None


class MissionCreate(BaseModel):
    project_id: UUID
    intent: str = Field(min_length=1, max_length=10_000)
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    target_role: str | None = Field(default=None, max_length=300)


class ResumeJdMissionCreate(BaseModel):
    project_id: UUID = Field(default_factory=uuid4)
    resume_text: str = Field(min_length=1, max_length=200_000)
    job_description: str = Field(min_length=1, max_length=200_000)


class TaskResponse(BaseModel):
    id: UUID
    mission_id: UUID
    name: str
    status: str
    result: dict | None = None
    error: str | None = None


class MissionEventResponse(BaseModel):
    id: UUID
    mission_id: UUID
    event_type: str
    timestamp: datetime
    detail: str


class ApprovalRequest(BaseModel):
    requested_action: str = Field(min_length=1, max_length=2000)
    risk_reason: str = Field(min_length=1, max_length=2000)
    required_by_policy: bool = False
    reviewer_id: str | None = Field(default=None, max_length=300)


class ApprovalDecisionUpdate(BaseModel):
    decision: ApprovalStatus = ApprovalStatus.PENDING
    reviewer_id: str | None = Field(default=None, max_length=300)
    reviewer_comment: str | None = Field(default=None, max_length=4000)


class ApprovalResponse(BaseModel):
    id: UUID
    mission_id: UUID
    task_id: UUID | None = None
    requested_action: str
    risk_reason: str
    required_by_policy: bool
    status: ApprovalStatus
    requested_at: datetime
    reviewed_at: datetime | None = None
    reviewer_id: str | None = None
    reviewer_comment: str | None = None
    expiration: datetime | None = None
    metadata: dict = Field(default_factory=dict)


class MissionDetailResponse(BaseModel):
    id: UUID
    project_id: UUID
    intent: str
    status: MissionStatus
    task: TaskResponse
    result: dict | None = None
    error: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    approval_required: bool = False
    events: list[MissionEventResponse] = Field(default_factory=list)
    approvals: list[ApprovalResponse] = Field(default_factory=list)


class MissionListResponse(BaseModel):
    id: UUID
    project_id: UUID
    intent: str
    status: MissionStatus
    task: TaskResponse
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    project_id: UUID
    total_missions: int
    running_missions: int
    completed_missions: int
    failed_missions: int
    blocked_missions: int
    recent_missions: list[MissionListResponse]


class MissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    intent: str
    execution_mode: ExecutionMode
    status: MissionStatus


class PolicyDecisionResponse(BaseModel):
    decision: PolicyDecision
    rule_id: str
    reason: str
    risk_level: RiskLevel
    approval_required: bool