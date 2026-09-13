from fastapi import FastAPI

from app.contracts.schemas import HealthResponse
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health/live", response_model=HealthResponse, tags=["health"])
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
def readiness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)