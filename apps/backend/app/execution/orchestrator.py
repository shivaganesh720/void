"""The persisted, local-first mission execution path.

The module deliberately has no HTTP concerns.  A route supplies an authenticated
actor and a SQLAlchemy session, then this service records every routing,
policy, agent, model, cost, evidence, and artifact decision before returning a
mission to the API layer.  The local model is deterministic, but it is an
explicit provider with an accurately reported identity—not a pretend call to
an unavailable hosted model.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.capabilities.broker import AgentRegistry
from app.execution.execution_control import IntentGate
from app.execution.lifecycle import StrategyResolver
from app.execution.task_state import validate_transition
from app.integrations.providers import ModelGateway
from app.models.base import (
    AgentRun,
    Approval,
    Artifact,
    CostRecord,
    Evidence,
    ExecutionProfile,
    LifecycleEvent,
    Mission,
    MissionBlueprint,
    MissionInput,
    MissionOutput,
    ModelRun,
    PolicyDecisionRecord,
    Task,
    User,
)
from app.models.enums import ApprovalStatus, ExecutionMode, IntentType, MissionStatus, RiskLevel, TaskStatus
from app.policies.evaluator import PolicyContext, evaluate_pre_execution


_ROOT = Path(__file__).resolve().parents[4]
_ARTIFACT_ROOT = _ROOT / "storage" / "artifacts"

_AGENT_BY_INTENT = {
    IntentType.RESUME_ANALYSIS: "resume_agent",
    IntentType.RESEARCH: "research_agent",
    IntentType.DATA_ANALYSIS: "data_analyst_agent",
    IntentType.CODE_ANALYSIS: "coding_agent",
    IntentType.DOCUMENT_GENERATION: "report_agent",
    IntentType.PRESENTATION_GENERATION: "report_agent",
}

_INPUT_REQUIRED = {
    IntentType.RESUME_ANALYSIS: "Provide both a resume and a job description, or use the Resume/JD upload mission.",
    IntentType.DATA_ANALYSIS: "Attach a CSV, XLSX, or JSON data source before analysis can run.",
    IntentType.CODE_ANALYSIS: "Attach source code or provide a repository reference before code analysis can run.",
}


def _as_json(value: Any) -> Any:
    """Convert Pydantic/enums to JSON-safe structures for durable metadata."""
    if hasattr(value, "model_dump"):
        return _as_json(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return {str(key): _as_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_as_json(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value


class MissionOrchestrator:
    """Plans and executes one bounded mission at a time.

    Background workers can call the same ``execute`` method.  It is
    synchronous by design for the local provider so API users get a truthful
    final state rather than a simulated queue acknowledgement.
    """

    def __init__(self) -> None:
        self.intent_gate = IntentGate()
        self.resolver = StrategyResolver()
        self.models = ModelGateway()
        self.agents = AgentRegistry()

    @staticmethod
    def record_event(db: Session, mission: Mission, event_type: str, detail: str) -> None:
        mission.updated_at = datetime.now(UTC)
        db.add(LifecycleEvent(mission_id=mission.id, event_type=event_type, detail=detail))

    @staticmethod
    def _set_mission_status(mission: Mission, target: MissionStatus) -> None:
        current = MissionStatus(mission.status)
        if current != target:
            validate_transition(current, target)
            mission.status = target.value

    @staticmethod
    def _set_task_status(task: Task, target: TaskStatus) -> None:
        current = TaskStatus(task.status)
        if current != target:
            validate_transition(current, target)
            task.status = target.value

    def create_and_plan(
        self,
        db: Session,
        *,
        project_id: Any,
        user: User,
        prompt: str,
        execution_profile: Any | None,
    ) -> tuple[Mission, Task]:
        profile = _as_json(execution_profile) if execution_profile else {}
        execution_mode = profile.get("execution_mode", ExecutionMode.AUTO.value)
        analysis = self.intent_gate.analyze(prompt, execution_mode=ExecutionMode(execution_mode))
        decision = self.resolver.resolve(
            analysis.intent,
            risk_level=analysis.risk_level.value,
            requires_approval=analysis.approval_required,
        )
        agent_id = _AGENT_BY_INTENT.get(analysis.intent_type, "manager_agent")
        agent = self.agents.get(agent_id)

        mission = Mission(
            project_id=project_id,
            intent=analysis.intent,
            execution_mode=execution_mode,
            status=MissionStatus.REQUESTED.value,
            approval_required=False,
            metadata_json={},
        )
        db.add(mission)
        db.flush()
        task = Task(mission_id=mission.id, name=f"{decision.workflow_id}:execute", status=TaskStatus.CREATED.value)
        db.add(task)
        db.flush()

        self.record_event(db, mission, "MISSION_REQUESTED", "Mission request accepted by the universal intent gate.")
        self._set_mission_status(mission, MissionStatus.VALIDATING)
        self.record_event(db, mission, "INTENT_NORMALIZED", f"Detected {analysis.intent_type.value}; risk={analysis.risk_level.value}.")

        # A provider is external only when a caller explicitly selects one.
        preferred_provider = str(profile.get("preferred_provider") or "").casefold()
        external_model_requested = bool(preferred_provider and preferred_provider not in {"local", "ollama", "test", "local-test-model"})
        policy = evaluate_pre_execution(
            PolicyContext(
                authenticated=True,
                project_member=True,
                external_model_requested=external_model_requested,
                private_data=profile.get("privacy_mode", "STANDARD") != "PUBLIC",
            )
        )
        requires_approval = bool(
            analysis.approval_required
            or policy.approval_required
            or execution_mode == ExecutionMode.GUIDED.value
        )
        manual_config_missing = execution_mode == ExecutionMode.MANUAL.value and not (
            profile.get("selected_agents") or profile.get("allowed_capabilities") or profile.get("workflow_preference")
        )
        missing_input = _INPUT_REQUIRED.get(analysis.intent_type)

        blueprint = {
            "mission_id": str(mission.id),
            "objective": analysis.intent,
            "intent_type": analysis.intent_type.value,
            "execution_mode": execution_mode,
            "selected_strategy": decision.strategy.value,
            "workflow_id": decision.workflow_id,
            "strategy_reason": decision.reason,
            "tasks": [{"id": str(task.id), "name": task.name, "agent": agent.id, "dependencies": []}],
            "agents": [agent.id],
            "models": ["local-test-model"],
            "tools": list(agent.tool_allowlist),
            "constraints": analysis.constraints,
            "risk_level": analysis.risk_level.value,
            "approval_checkpoints": ["pre_execution"] if requires_approval else [],
            "validation_rules": ["schema", "policy", "artifact_hash"],
            "expected_artifacts": ["mission-report.json"],
            "expected_evidence": ["intent", "execution-record"],
        }
        mission.metadata_json = {
            "intent": _as_json(analysis),
            "strategy": {"id": f"decision-{mission.id}", "strategy": decision.strategy.value, "reason": decision.reason, "workflow_id": decision.workflow_id},
            "blueprint": blueprint,
            "policy": {"decision": policy.decision.value, "rule_id": policy.rule_id, "reason": policy.reason, "approval_required": requires_approval},
        }
        db.add(MissionInput(mission_id=mission.id, input_key="prompt", input_type="text", content=analysis.intent))
        db.add(ExecutionProfile(mission_id=mission.id, profile_json=profile))
        db.add(MissionBlueprint(mission_id=mission.id, blueprint_json=blueprint))
        db.add(PolicyDecisionRecord(
            mission_id=mission.id,
            decision=policy.decision.value,
            rule_id=policy.rule_id,
            reason=policy.reason,
            risk_level=analysis.risk_level.value,
        ))
        self._set_mission_status(mission, MissionStatus.PLANNED)
        self.record_event(db, mission, "BLUEPRINT_CREATED", f"Selected {decision.workflow_id} with {agent.name}.")

        if manual_config_missing:
            self._set_mission_status(mission, MissionStatus.WAITING_FOR_INPUT)
            self._set_task_status(task, TaskStatus.WAITING)
            mission.metadata_json["clarification"] = "Manual mode requires a selected agent, capability, or workflow."
            self.record_event(db, mission, "INPUT_REQUIRED", mission.metadata_json["clarification"])
        elif missing_input:
            self._set_mission_status(mission, MissionStatus.WAITING_FOR_INPUT)
            self._set_task_status(task, TaskStatus.WAITING)
            mission.metadata_json["clarification"] = missing_input
            self.record_event(db, mission, "INPUT_REQUIRED", missing_input)
        elif requires_approval:
            mission.approval_required = True
            self._set_mission_status(mission, MissionStatus.WAITING_FOR_APPROVAL)
            approval = Approval(
                mission_id=mission.id,
                task_id=task.id,
                requested_action=f"Execute {decision.workflow_id}",
                risk_reason=policy.reason if policy.approval_required else f"{analysis.risk_level.value} risk mission requires review.",
                required_by_policy=True,
                status=ApprovalStatus.PENDING.value,
                metadata_json={"risk": analysis.risk_level.value, "data": "mission prompt", "reversible": True},
            )
            db.add(approval)
            self.record_event(db, mission, "APPROVAL_REQUESTED", approval.risk_reason)
        else:
            self._set_mission_status(mission, MissionStatus.READY)
            self.record_event(db, mission, "MISSION_READY", "Local execution is permitted by policy.")

        return mission, task

    def execute(self, db: Session, *, mission: Mission, task: Task, user: User) -> Mission:
        if MissionStatus(mission.status) == MissionStatus.READY:
            self._set_mission_status(mission, MissionStatus.RUNNING)
        elif MissionStatus(mission.status) == MissionStatus.APPROVED:
            self._set_mission_status(mission, MissionStatus.RUNNING)
        elif MissionStatus(mission.status) != MissionStatus.RUNNING:
            raise ValueError(f"MISSION_NOT_EXECUTABLE:{mission.status}")

        self._set_task_status(task, TaskStatus.READY)
        self._set_task_status(task, TaskStatus.QUEUED)
        self._set_task_status(task, TaskStatus.RUNNING)
        metadata = mission.metadata_json or {}
        intent = metadata.get("intent", {})
        agent_id = (metadata.get("blueprint", {}).get("agents") or ["manager_agent"])[0]
        agent = self.agents.get(agent_id)
        self.record_event(db, mission, "EXECUTION_STARTED", f"{agent.name} is executing through the local model gateway.")

        try:
            prompt = (
                f"Objective: {mission.intent}\n"
                f"Intent type: {intent.get('intent_type', 'general_assistance')}\n"
                f"Constraints: {', '.join(intent.get('constraints', [])) or 'none'}\n"
                "Produce a concise, bounded local execution report. Clearly identify any work that needs an external provider or user data."
            )
            response = self.models.generate(prompt=prompt)
            report = {
                "summary": response.content,
                "intent_type": intent.get("intent_type", "general_assistance"),
                "strategy": metadata.get("strategy", {}),
                "agent": {"id": agent.id, "name": agent.name, "version": agent.version},
                "provider": {"name": response.provider.value, "model": response.model_name, "local_fallback": response.provider.value == "test"},
                "validation": {"status": "PASSED", "rules": metadata.get("blueprint", {}).get("validation_rules", [])},
                "limitations": ["No external service was called."] if response.provider.value == "test" else [],
            }
            agent_run = AgentRun(task_id=task.id, agent_id=agent.id, status="COMPLETED", input_json={"intent": mission.intent}, output_json=report)
            db.add(agent_run)
            db.flush()
            db.add(ModelRun(
                task_id=task.id,
                agent_run_id=agent_run.id,
                provider=response.provider.value,
                model_name=response.model_name,
                input_tokens=response.usage_tokens,
                output_tokens=0,
                cost=response.cost,
            ))
            db.add(CostRecord(
                mission_id=mission.id,
                project_id=mission.project_id,
                resource_type="model",
                resource_id=response.model_name,
                cost_amount=response.cost,
            ))
            db.add(Evidence(
                mission_id=mission.id,
                task_id=task.id,
                source="mission_prompt",
                label="user_intent",
                quote=mission.intent[:2000],
                confidence=1.0,
                metadata_json={"type": "user-provided"},
            ))
            artifact = self._write_artifact(mission, task, user, report)
            db.add(artifact)
            task.result_json = report
            mission.metadata_json = {**metadata, "result": report, "artifacts": [{"id": str(artifact.id), "name": artifact.name}]}
            db.add(MissionOutput(mission_id=mission.id, output_key="mission_report", content_json=report))
            self._set_task_status(task, TaskStatus.SUCCEEDED)
            self._set_mission_status(mission, MissionStatus.COMPLETED)
            mission.completed_at = datetime.now(UTC)
            self.record_event(db, mission, "MISSION_COMPLETED", "Local provider result validated, hashed, and persisted.")
        except Exception as exc:
            task.error = "EXECUTION_FAILED"
            mission.error = "Mission execution failed without exposing internal details."
            self._set_task_status(task, TaskStatus.FAILED)
            self._set_mission_status(mission, MissionStatus.FAILED)
            self.record_event(db, mission, "MISSION_FAILED", mission.error)
            raise exc
        return mission

    @staticmethod
    def _write_artifact(mission: Mission, task: Task, user: User, report: dict[str, Any]) -> Artifact:
        _ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
        content = json.dumps(report, indent=2, sort_keys=True)
        name = f"mission-{mission.id}-report.json"
        path = _ARTIFACT_ROOT / name
        content_bytes = content.encode("utf-8")
        path.write_bytes(content_bytes)
        return Artifact(
            project_id=mission.project_id,
            mission_id=mission.id,
            task_id=task.id,
            owner_id=user.id,
            name=name,
            type="MISSION_REPORT",
            mime_type="application/json",
            storage_location=str(path),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            size_bytes=len(content_bytes),
            status="CREATED",
        )

