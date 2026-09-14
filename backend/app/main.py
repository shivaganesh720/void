import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import auth, projects, missions, admin, health, approvals, gateways, knowledge, workflows, websockets, memory, companion

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
logger = logging.getLogger("void.execution")

from app.api.middleware import AuditMiddleware

app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Phase 1 routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(missions.router)
app.include_router(admin.router, prefix="/api/v1")

# Phase 2 routers
app.include_router(approvals.router)
app.include_router(gateways.router)
app.include_router(knowledge.router)
app.include_router(workflows.router)
app.include_router(websockets.router)
app.include_router(memory.router, prefix="/api/v1")
app.include_router(companion.router)