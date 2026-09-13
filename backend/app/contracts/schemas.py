from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.enums import ApprovalStatus, ExecutionMode, IntentType, MissionStatus, ModelMode, PolicyDecision, RiskLevel, StrategyType


class ExecutionProfileRequest(BaseModel):
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    model_mode: ModelMode = ModelMode.AUTO
    preferred_provider: str | None = Field(default=None, max_length=200)
    fallback_providers: list[str] = Field(default_factory=list)
    selected_agents: list[str] = Field(default_factory=list)
    allowed_capabilities: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    workflow_preference: str | None = Field(default=None, max_length=200)
    validation_level: str = "STANDARD"
    budget_limits: dict = Field(default_factory=dict)
    token_limits: dict = Field(default_factory=dict)
    time_limits: dict = Field(default_factory=dict)
    retry_limits: dict = Field(default_factory=dict)
    privacy_mode: str = "STANDARD"
    research_permissions: bool = False
    memory_permissions: bool = True
    artifact_preferences: dict = Field(default_factory=dict)
    approval_preferences: dict = Field(default_factory=dict)
    explanation_detail_level: str = "STANDARD"


class RegisterRequest(BaseModel):
    full_name: str = Field(default="", max_length=200)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    role: str = "USER"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=4096)


class UserSummaryResponse(BaseModel):
    id: UUID
    email: str
    role: str
    full_name: str = ""
    onboarding_completed: bool = False
    created_at: datetime | None = None


class ProfileUpdateRequest(BaseModel):
    ai_awareness: str = Field(default="AI_UNAWARE", pattern="^(AI_UNAWARE|AI_AWARE)$")
    default_mode: str = Field(default="AUTO", pattern="^(AUTO|GUIDED|MANUAL)$")
    explanation_level: str = Field(default="STANDARD", pattern="^(SIMPLE|STANDARD|TECHNICAL)$")
    execution_priority: str = Field(default="QUALITY", pattern="^(QUALITY|SPEED|COST|PRIVACY)$")


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    members: list[UUID] = Field(default_factory=list)
    created_at: datetime | None = None


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
    execution_profile: ExecutionProfileRequest | None = None


class ResumeJdMissionCreate(BaseModel):
    project_id: UUID = Field(default_factory=uuid4)
    resume_text: str = Field(min_length=1, max_length=200_000)
    job_description: str = Field(min_length=1, max_length=200_000)
    execution_profile: ExecutionProfileRequest | None = None


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
    execution_profile: ExecutionProfileRequest | None = None
    approval_required: bool = False
    events: list[MissionEventResponse] = Field(default_factory=list)
    approvals: list[ApprovalResponse] = Field(default_factory=list)


class MissionListResponse(BaseModel):
    id: UUID
    project_id: UUID
    intent: str
    status: MissionStatus
    task: TaskResponse
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    created_at: datetime


class ExplanationReportResponse(BaseModel):
    mission_id: UUID
    project_id: UUID
    summary: dict
    execution_steps: list[dict] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    artifacts: list[dict] = Field(default_factory=list)
    created_at: datetime | None = None


class DashboardSummaryResponse(BaseModel):
    project_id: UUID
    total_missions: int
    running_missions: int
    completed_missions: int
    failed_missions: int
    blocked_missions: int
    recent_missions: list[MissionListResponse]


class AdminOverviewResponse(BaseModel):
    user_count: int
    admin_count: int
    auditor_count: int
    project_count: int
    mission_count: int


class AdminUserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    full_name: str = ""
    onboarding_completed: bool = False
    created_at: datetime | None = None


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


class MissionRequest(BaseModel):
    project_id: UUID | None = None
    intent: str = Field(min_length=1, max_length=10_000)
    intent_type: IntentType = IntentType.GENERAL_ASSISTANCE
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    strategy: StrategyType | None = None
    entities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    approval_required: bool = False
    risk_level: RiskLevel = RiskLevel.MEDIUM
    context: dict = Field(default_factory=dict)
    input_files: list[str] = Field(default_factory=list)


class MissionContext(BaseModel):
    project_id: UUID | None = None
    user_id: UUID | None = None
    requested_by: str | None = None
    execution_mode: ExecutionMode = ExecutionMode.AUTO
    privacy_mode: str = "STANDARD"
    budget_limit: float | None = None
    time_limit_seconds: int | None = None
    metadata: dict = Field(default_factory=dict)


class CapabilityDescriptor(BaseModel):
    name: str
    slug: str
    version: str = "1.0"
    description: str = ""
    required_models: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    supported_file_types: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    privacy_level: str = "STANDARD"
    enabled: bool = True
    validation_requirements: list[str] = Field(default_factory=list)


class CapabilityRequest(BaseModel):
    intent: str
    intent_type: IntentType = IntentType.GENERAL_ASSISTANCE
    required_capabilities: list[str] = Field(default_factory=list)
    requested_tools: list[str] = Field(default_factory=list)
    file_types: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM


class ExecutionPlan(BaseModel):
    strategy: StrategyType
    workflow_id: str
    steps: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    rationale: str = ""


class MissionBlueprint(BaseModel):
    mission_id: UUID | None = None
    intent: str
    intent_type: IntentType
    strategy: StrategyType
    capabilities: list[str] = Field(default_factory=list)
    plan: ExecutionPlan | None = None


class TaskDefinition(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    task_type: str = "generic"
    dependencies: list[UUID] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    timeout_seconds: int | None = None
    retry_limit: int = 0


class TaskState(BaseModel):
    id: UUID
    name: str
    status: str = "CREATED"
    retry_count: int = 0
    error: str | None = None
    result: dict | None = None


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class EvidenceRecord(BaseModel):
    source: str
    title: str
    excerpt: str = ""
    confidence: float = 0.0
    relevance: float = 0.0
    page_number: int | None = None


class CostRecord(BaseModel):
    amount: float = 0.0
    currency: str = "USD"
    source: str = "internal"


class MemoryRecord(BaseModel):
    key: str
    value: str
    project_id: UUID | None = None
    approved: bool = False


class KnowledgeRecord(BaseModel):
    title: str
    source: str
    content: str = ""
    project_id: UUID | None = None