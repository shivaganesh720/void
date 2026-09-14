import pytest

from app.models.enums import ExecutionMode, PolicyDecision
from app.policies.evaluator import PolicyContext, evaluate_pre_execution
from app.execution.scheduler import resolve_strategy


def test_private_external_model_requires_approval() -> None:
    result = evaluate_pre_execution(PolicyContext(True, True, external_model_requested=True))
    assert result.decision is PolicyDecision.APPROVAL
    assert result.approval_required is True


def test_strategy_selects_only_bounded_resume_workflow() -> None:
    result = resolve_strategy("Compare my resume with this job description", ExecutionMode.AUTO)
    assert result.workflow_id == "resume_jd_intelligence_v1"
    assert "DOCUMENT_PARSE" in result.capabilities


def test_unknown_strategy_is_rejected() -> None:
    with pytest.raises(ValueError, match="CAPABILITY_UNAVAILABLE"):
        resolve_strategy("Send an email", ExecutionMode.AUTO)