import pytest

from app.contracts.enums import ExecutionMode, IntentType, RiskLevel, StrategyType
from app.control_plane.capabilities import CapabilityRegistry
from app.control_plane.engine import StrategyResolver
from app.control_plane.intent import IntentGate


def test_intent_gate_detects_resume_analysis() -> None:
    mission = IntentGate().analyze("Compare my resume with this job description", execution_mode=ExecutionMode.AUTO)
    assert mission.intent_type is IntentType.RESUME_ANALYSIS
    assert mission.strategy is StrategyType.RESEARCH_AND_VALIDATE
    assert mission.approval_required is False


def test_capability_registry_lists_enabled_capabilities() -> None:
    registry = CapabilityRegistry()
    capabilities = registry.find_matching(["resume_intelligence", "data_analysis", "code_analysis"])
    assert {cap.slug for cap in capabilities} == {"resume_intelligence", "data_analysis", "code_analysis"}


def test_strategy_resolver_uses_minimal_workflow_for_data_intent() -> None:
    decision = StrategyResolver().resolve("Analyze the sales CSV and summarize trends")
    assert decision.workflow_id == "data_analysis_v1"
    assert decision.strategy is StrategyType.DATA_ANALYSIS_PIPELINE


def test_unknown_capability_raises() -> None:
    registry = CapabilityRegistry()
    with pytest.raises(KeyError, match="CAPABILITY_NOT_FOUND"):
        registry.get("not_real")
