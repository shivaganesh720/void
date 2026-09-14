from fastapi import APIRouter, Depends
from app.integrations.base import SafeToolGateway
from app.integrations.providers import ModelGateway
from app.api.deps import get_current_user

router = APIRouter(tags=["gateways"])
tool_gateway = SafeToolGateway()
model_gateway = ModelGateway()

@router.get("/api/v1/tools")
def list_tools(current_user=Depends(get_current_user)):
    return tool_gateway.list_tools()

@router.get("/api/v1/models")
def list_models(current_user=Depends(get_current_user)):
    return model_gateway.list_models()
