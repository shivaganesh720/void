import pytest

from app.gateways.tool_gateway import SafeToolGateway, ToolDefinition, ToolExecutionContext, ToolRisk


def test_safe_tool_gateway_allows_low_risk_tool_for_member() -> None:
    gateway = SafeToolGateway()

    def read_file(payload: dict, context: ToolExecutionContext) -> dict:
        return {"path": payload["path"], "owner": context.user_id}

    gateway.register(
        ToolDefinition(
            name="read_file",
            description="Read a project artifact",
            risk_level=ToolRisk.LOW,
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        ),
        executor=read_file,
    )

    result = gateway.execute(
        "read_file",
        {"path": "docs/brief.md"},
        ToolExecutionContext(user_id="user-1", project_id="project-1", authenticated=True, project_member=True),
    )

    assert result["ok"] is True
    assert result["output"]["path"] == "docs/brief.md"
    assert result["risk_level"] == ToolRisk.LOW.value


def test_safe_tool_gateway_blocks_high_risk_tool_without_approval() -> None:
    gateway = SafeToolGateway()

    gateway.register(
        ToolDefinition(
            name="delete_project",
            description="Delete an entire project",
            risk_level=ToolRisk.CRITICAL,
            requires_approval=True,
            input_schema={"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]},
        ),
        executor=lambda payload, context: {"status": "deleted"},
    )

    with pytest.raises(PermissionError):
        gateway.execute(
            "delete_project",
            {"project_id": "project-1"},
            ToolExecutionContext(user_id="user-1", project_id="project-1", authenticated=True, project_member=True),
        )


def test_safe_tool_gateway_rejects_invalid_payload() -> None:
    gateway = SafeToolGateway()
    gateway.register(
        ToolDefinition(
            name="search_docs",
            description="Search project docs",
            risk_level=ToolRisk.MEDIUM,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        ),
        executor=lambda payload, context: {"matches": payload["query"]},
    )

    with pytest.raises(ValueError):
        gateway.execute(
            "search_docs",
            {"bad": "value"},
            ToolExecutionContext(user_id="user-1", project_id="project-1", authenticated=True, project_member=True),
        )
