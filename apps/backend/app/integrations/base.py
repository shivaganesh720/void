from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import csv
import io
from typing import Any, Callable


class ToolRisk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ToolExecutionContext:
    user_id: str
    project_id: str
    authenticated: bool = False
    project_member: bool = False
    approval_granted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    risk_level: ToolRisk
    input_schema: dict[str, Any]
    version: str = "1.0"
    output_schema: dict[str, Any] = field(default_factory=lambda: {"type": "object"})
    permission_requirements: tuple[str, ...] = ("project:execute",)
    privacy_level: str = "STANDARD"
    allowed_agents: tuple[str, ...] = ()
    allowed_execution_modes: tuple[str, ...] = ("AUTO", "GUIDED", "MANUAL")
    timeout_seconds: int = 30
    rate_limit_per_minute: int = 30
    estimated_cost: float = 0.0
    requires_approval: bool = False
    enabled: bool = True


class SafeToolGateway:
    """Execute only validated, gated tools with project-scoped safeguards."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._executors: dict[str, Callable[[dict[str, Any], ToolExecutionContext], Any]] = {}

    def register(self, definition: ToolDefinition, *, executor: Callable[[dict[str, Any], ToolExecutionContext], Any]) -> None:
        self._tools[definition.name] = definition
        self._executors[definition.name] = executor

    def _validate_payload(self, definition: ToolDefinition, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError("Tool payload must be an object.")
        required = definition.input_schema.get("required", [])
        for field_name in required:
            if field_name not in payload:
                raise ValueError(f"Missing required field: {field_name}")
        properties = definition.input_schema.get("properties", {})
        for key, value in payload.items():
            expected = properties.get(key)
            if expected is None:
                continue
            expected_type = expected.get("type")
            if expected_type == "string" and not isinstance(value, str):
                raise ValueError(f"Field '{key}' must be a string.")
            if expected_type == "integer" and not isinstance(value, int):
                raise ValueError(f"Field '{key}' must be an integer.")

    def execute(self, tool_name: str, payload: dict[str, Any], context: ToolExecutionContext) -> dict[str, Any]:
        definition = self._tools.get(tool_name)
        if definition is None:
            raise KeyError(f"Tool '{tool_name}' is not registered.")
        if not definition.enabled:
            raise PermissionError(f"Tool '{tool_name}' is disabled.")
        if not context.authenticated:
            raise PermissionError("Authentication required.")
        if not context.project_member:
            raise PermissionError("Project membership required.")
        if definition.requires_approval and not context.approval_granted:
            raise PermissionError(f"Tool '{tool_name}' requires approval before execution.")

        self._validate_payload(definition, payload)
        executor = self._executors[tool_name]
        output = executor(payload, context)
        return {
            "ok": True,
            "tool": tool_name,
            "risk_level": definition.risk_level.value,
            "output": output,
        }

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())


def build_local_tool_gateway() -> SafeToolGateway:
    """Register local adapters whose behavior is safe and executable offline.

    Network, mail, browser, and desktop integrations are intentionally not
    registered as enabled tools until a provider connection is configured.
    This prevents a catalog entry from masquerading as a successful external
    integration.
    """
    gateway = SafeToolGateway()
    gateway.register(
        ToolDefinition(
            name="document_parse",
            description="Extract simple structural facts from supplied text.",
            risk_level=ToolRisk.LOW,
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
            allowed_agents=("resume_agent", "document_agent", "evidence_agent"),
        ),
        executor=lambda payload, _context: {"characters": len(payload["text"]), "lines": len(payload["text"].splitlines()), "preview": payload["text"][:500]},
    )
    gateway.register(
        ToolDefinition(
            name="csv_inspect",
            description="Inspect a CSV payload locally without executing code.",
            risk_level=ToolRisk.LOW,
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
            allowed_agents=("data_analyst_agent",),
        ),
        executor=lambda payload, _context: _inspect_csv(payload["text"]),
    )
    gateway.register(
        ToolDefinition(
            name="text_classify",
            description="Perform deterministic local text classification metadata extraction.",
            risk_level=ToolRisk.LOW,
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
            allowed_agents=("manager_agent", "document_agent"),
        ),
        executor=lambda payload, _context: {"word_count": len(payload["text"].split()), "empty": not bool(payload["text"].strip())},
    )
    return gateway


def _inspect_csv(text: str) -> dict[str, Any]:
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[0] if rows else []
    return {"columns": header, "column_count": len(header), "row_count": max(0, len(rows) - 1)}
