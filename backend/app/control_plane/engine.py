from dataclasses import dataclass, field
from uuid import uuid4

from app.contracts.enums import StrategyType


@dataclass(frozen=True)
class Decision:
    strategy: StrategyType
    workflow_id: str
    reason: str
    approval_required: bool = False


@dataclass
class MissionBlueprint:
    mission_id: str
    intent: str
    strategy: StrategyType
    steps: list[str] = field(default_factory=list)
    approval_required: bool = False


class StrategyResolver:
    """Select the minimal complexity strategy that fits the intent."""

    def resolve(self, intent: str, *, risk_level: str | None = None, requires_approval: bool = False) -> Decision:
        normalized = intent.casefold()
        if any(term in normalized for term in ("resume", "cv", "job description", "jd")):
            return Decision(
                strategy=StrategyType.RESEARCH_AND_VALIDATE,
                workflow_id="resume_jd_intelligence_v1",
                reason="resume_jd_match",
                approval_required=requires_approval,
            )
        if any(term in normalized for term in ("data", "csv", "xlsx", "chart", "statistics")):
            return Decision(
                strategy=StrategyType.DATA_ANALYSIS_PIPELINE,
                workflow_id="data_analysis_v1",
                reason="data_analysis_match",
                approval_required=requires_approval,
            )
        if any(term in normalized for term in ("code", "python", "javascript", "typescript", "java", "sql")):
            return Decision(
                strategy=StrategyType.TOOL_ASSISTED,
                workflow_id="code_intelligence_v1",
                reason="code_analysis_match",
                approval_required=requires_approval,
            )
        if any(term in normalized for term in ("document", "write", "draft", "report", "presentation")):
            return Decision(
                strategy=StrategyType.DOCUMENT_PIPELINE,
                workflow_id="document_pipeline_v1",
                reason="document_generation_match",
                approval_required=requires_approval,
            )
        if any(term in normalized for term in ("research", "source", "evidence")):
            return Decision(
                strategy=StrategyType.RESEARCH_AND_VALIDATE,
                workflow_id="research_evidence_v1",
                reason="research_match",
                approval_required=requires_approval,
            )
        return Decision(
            strategy=StrategyType.SINGLE_MODEL,
            workflow_id="general_assistance_v1",
            reason="default_minimal_strategy",
            approval_required=requires_approval,
        )

    def build_blueprint(self, mission_id: str, intent: str, *, risk_level: str | None = None, requires_approval: bool = False) -> MissionBlueprint:
        decision = self.resolve(intent, risk_level=risk_level, requires_approval=requires_approval)
        steps = [
            "normalize_intent",
            "validate_inputs",
            "select_capabilities",
            "execute_strategy",
            "validate_output",
        ]
        return MissionBlueprint(
            mission_id=mission_id,
            intent=intent,
            strategy=decision.strategy,
            steps=steps,
            approval_required=decision.approval_required,
        )
