import pytest

from app.workflows.engine import ArtifactRecord, EvidenceRecord, WorkflowExecutionEngine, WorkflowPlan


def test_workflow_engine_executes_steps_and_collects_artifacts() -> None:
    engine = WorkflowExecutionEngine()
    plan = WorkflowPlan(
        mission_id="mission-123",
        intent="Analyze a resume against a job description",
        steps=["normalize_intent", "validate_inputs", "execute_analysis"],
        required_capabilities=["resume_analysis"],
        approval_required=False,
    )

    result = engine.execute(plan)

    assert result["status"] == "completed"
    assert result["evidence"]
    assert any(item["type"] == "artifact" for item in result["artifacts"])


def test_workflow_engine_blocks_approval_required_plan() -> None:
    engine = WorkflowExecutionEngine()
    plan = WorkflowPlan(
        mission_id="mission-456",
        intent="Delete project data",
        steps=["confirm_scope", "execute_delete"],
        required_capabilities=["project_management"],
        approval_required=True,
    )

    with pytest.raises(PermissionError):
        engine.execute(plan, approval_granted=False)


def test_workflow_engine_records_failure_with_reason() -> None:
    engine = WorkflowExecutionEngine()
    plan = WorkflowPlan(
        mission_id="mission-789",
        intent="Run a failing workflow",
        steps=["validate_inputs", "fail_step"],
        required_capabilities=["testing"],
        approval_required=False,
    )

    result = engine.execute(plan, step_handlers={"fail_step": lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("forced failure"))})

    assert result["status"] == "failed"
    assert "forced failure" in result["error"]
