import pytest

from app.models.enums import ExecutionMode, IntentType, RiskLevel, StrategyType
from app.capabilities.registry import CapabilityRegistry
from app.execution.lifecycle import StrategyResolver
from app.execution.execution_control import IntentGate
from app.execution.mission_kernel import TaskNode, WorkGraph
from uuid import uuid4


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


def test_work_graph_rejects_missing_dependencies() -> None:
    task_id = uuid4()
    graph = WorkGraph(mission_id=uuid4())
    graph.add_task(TaskNode(id=task_id, name="child", dependencies=[uuid4()]))

    with pytest.raises(ValueError, match="INVALID_DEPENDENCY"):
        graph.get_ready_tasks()


def test_work_graph_rejects_cycles() -> None:
    first_id = uuid4()
    second_id = uuid4()
    graph = WorkGraph(mission_id=uuid4())
    graph.add_task(TaskNode(id=first_id, name="first", dependencies=[second_id]))
    graph.add_task(TaskNode(id=second_id, name="second", dependencies=[first_id]))

    with pytest.raises(ValueError, match="WORK_GRAPH_CYCLE"):
        graph.get_ready_tasks()
