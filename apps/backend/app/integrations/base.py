from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
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
