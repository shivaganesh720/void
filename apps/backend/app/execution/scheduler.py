from dataclasses import dataclass

from app.models.enums import ExecutionMode


@dataclass(frozen=True)
class StrategyDecision:
    workflow_id: str
    reason_code: str
    explanation: str
    requires_approval: bool
    capabilities: tuple[str, ...]


def resolve_strategy(intent: str, execution_mode: ExecutionMode) -> StrategyDecision:
    normalized = intent.casefold()
    resume_terms = ("resume", "cv")
    job_terms = ("job description", "job posting", "jd", "role")
    if any(term in normalized for term in resume_terms) and any(term in normalized for term in job_terms):
        return StrategyDecision(
            "resume_jd_intelligence_v1",
            "RESUME_JD_MATCH",
            f"Selected the minimum sufficient fixed workflow for {execution_mode.value} execution.",
            False,
            ("DOCUMENT_PARSE", "SKILL_NORMALIZATION", "EVIDENCE_VALIDATION", "REPORT_GENERATION"),
        )
    raise ValueError("CAPABILITY_UNAVAILABLE: no bounded V1 workflow matches this intent")