from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class WorkflowPlan:
    mission_id: str
    intent: str
    steps: list[str]
    required_capabilities: list[str] | None = None
    approval_required: bool = False


@dataclass(frozen=True)
class EvidenceRecord:
    source: str
    title: str
    detail: str
    confidence: float = 1.0


@dataclass(frozen=True)
class ArtifactRecord:
    name: str
    kind: str
    status: str = "created"
    metadata: dict[str, Any] = field(default_factory=dict)


class WorkflowExecutionEngine:
    """Execute bounded workflows while recording evidence and artifacts."""

    def __init__(self) -> None:
        self.default_handlers: dict[str, Callable[..., Any]] = {
            "normalize_intent": lambda *args, **kwargs: {"normalized": True},
            "validate_inputs": lambda *args, **kwargs: {"validated": True},
            "execute_analysis": lambda *args, **kwargs: {"result": "analysis_complete"},
            "confirm_scope": lambda *args, **kwargs: {"scope_confirmed": True},
            "execute_delete": lambda *args, **kwargs: {"result": "delete_complete"},
            "fail_step": lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("forced failure")),
        }

    def execute(self, plan: WorkflowPlan, *, approval_granted: bool = True, step_handlers: dict[str, Callable[..., Any]] | None = None) -> dict[str, Any]:
        if plan.approval_required and not approval_granted:
            raise PermissionError(f"Workflow '{plan.mission_id}' requires approval before execution.")

        handlers = {**self.default_handlers, **(step_handlers or {})}
        evidence: list[dict[str, Any]] = []
        artifacts: list[dict[str, Any]] = []

        for step in plan.steps:
            handler = handlers.get(step)
            if handler is None:
                result = {"step": step, "status": "skipped"}
            else:
                try:
                    result = handler(plan, step)
                except Exception as exc:
                    return {
                        "mission_id": plan.mission_id,
                        "status": "failed",
                        "error": str(exc),
                        "evidence": evidence,
                        "artifacts": artifacts,
                    }
            evidence.append({"type": "evidence", "source": step, "detail": str(result), "confidence": 1.0})
            artifacts.append({"type": "artifact", "name": f"{step}_artifact", "status": "created", "metadata": {"step": step}})

        return {
            "mission_id": plan.mission_id,
            "status": "completed",
            "intent": plan.intent,
            "evidence": evidence,
            "artifacts": artifacts,
            "error": None,
        }
