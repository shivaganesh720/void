from fastapi import APIRouter
from app.schemas import HealthResponse
from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()

@router.get("/health/live", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)

@router.get("/health/ready", response_model=HealthResponse)
def readiness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)
