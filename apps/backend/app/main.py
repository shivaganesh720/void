import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1 import auth, projects, missions, admin, health, approvals, gateways, knowledge, workflows, websockets, memory, companion

settings = get_settings()
from contextlib import asynccontextmanager
from app.db.session import database_health_check, initialize_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test DB connection and initialize safely
    try:
        if not database_health_check(settings.database_url):
            logger.error("Failed to connect to the database. Invalid configuration.")
            raise RuntimeError("Database connection failed. Please check configuration.")
        initialize_database(settings.database_url)
    except Exception as e:
        logger.error("Database initialization failed. Please check configuration.")
        raise RuntimeError("Database startup error.") from None
    yield

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
logger = logging.getLogger("void.execution")

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = str(exc.detail) if isinstance(exc.detail, str) and "_" in exc.detail else "API_ERROR"
    msg = exc.detail if isinstance(exc.detail, str) else "An unexpected error occurred."
    
    if exc.detail == "AUTH_INVALID_CREDENTIALS":
        msg = "Invalid email or password."
    elif exc.detail == "AUTH_INVALID_TOKEN":
        msg = "Invalid or expired session token."
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            # Retain FastAPI's conventional field for clients that have not
            # adopted the structured control-plane envelope yet.
            "detail": exc.detail,
            "error": {
                "code": code,
                "message": msg,
                "details": {},
                "request_id": str(uuid.uuid4())
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            # Keep FastAPI's interoperable validation contract as well as the
            # stable platform error envelope.  Clients can highlight a field
            # without parsing a human-readable message.
            "detail": exc.errors(),
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload.",
                "details": exc.errors(),
                "request_id": str(uuid.uuid4())
            }
        }
    )

from app.middleware import AuditMiddleware

app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
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
