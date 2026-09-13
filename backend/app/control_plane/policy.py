from dataclasses import dataclass

from app.contracts.enums import PolicyDecision, RiskLevel


@dataclass(frozen=True)
class PolicyContext:
    authenticated: bool
    project_member: bool
    external_model_requested: bool = False
    private_data: bool = True
    artifact_valid: bool = False


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    rule_id: str
    reason: str
    risk_level: RiskLevel
    approval_required: bool = False


def evaluate_pre_execution(context: PolicyContext) -> PolicyResult:
    if not context.authenticated:
        return PolicyResult(PolicyDecision.BLOCK, "AUTH_REQUIRED", "Authentication is required.", RiskLevel.HIGH)
    if not context.project_member:
        return PolicyResult(PolicyDecision.BLOCK, "PROJECT_ACCESS", "The actor is not a member of this project.", RiskLevel.HIGH)
    if context.external_model_requested and context.private_data:
        return PolicyResult(
            PolicyDecision.APPROVAL,
            "PRIVATE_EXTERNAL_MODEL",
            "Private project data requires approval before external model use.",
            RiskLevel.HIGH,
            approval_required=True,
        )
    return PolicyResult(PolicyDecision.ALLOW, "V1_LOCAL_WORKFLOW", "The bounded local workflow is permitted.", RiskLevel.LOW)