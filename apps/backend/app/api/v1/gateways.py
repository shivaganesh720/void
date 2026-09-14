from dataclasses import asdict

from fastapi import APIRouter, Depends
from app.capabilities.broker import AgentRegistry
from app.capabilities.registry import CapabilityRegistry
from app.integrations.base import SafeToolGateway, ToolExecutionContext, build_local_tool_gateway
from app.integrations.providers import ModelGateway
from app.api.deps import get_current_user

router = APIRouter(tags=["gateways"])
tool_gateway = build_local_tool_gateway()
model_gateway = ModelGateway()
capability_registry = CapabilityRegistry()
agent_registry = AgentRegistry()

@router.get("/api/v1/tools")
def list_tools(current_user=Depends(get_current_user)):
    return [asdict(tool) for tool in tool_gateway.list_tools()]

@router.get("/api/v1/models")
def list_models(current_user=Depends(get_current_user)):
    return model_gateway.list_models()


@router.get("/api/v1/capabilities")
def list_capabilities(current_user=Depends(get_current_user)):
    return [asdict(capability) for capability in capability_registry.list()]


@router.get("/api/v1/agents")
def list_agents(current_user=Depends(get_current_user)):
    return [asdict(agent) for agent in agent_registry.list()]
