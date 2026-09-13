from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.enums import ExecutionMode, MissionStatus, PolicyDecision, RiskLevel


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