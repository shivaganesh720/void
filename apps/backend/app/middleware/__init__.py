import json
import time
from uuid import UUID
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.base import AuditEvent
from app.api.deps import DEFAULT_DEMO_USER_ID

logger = logging.getLogger("void.audit")


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all mutating API requests (POST, PUT, PATCH, DELETE)
    to the AuditEvent table if a project_id is present in the query parameters.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        project_id_str = request.query_params.get("project_id")
        if not project_id_str and request.headers.get("content-type", "").split(";", 1)[0].lower() == "application/json":
            body = await request.body()
            if body:
                try:
                    project_id_str = json.loads(body).get("project_id")
                except (json.JSONDecodeError, AttributeError, TypeError):
                    project_id_str = None

            received = False

            async def replay_body():
                nonlocal received
                if received:
                    return {"type": "http.request", "body": b"", "more_body": False}
                received = True
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = replay_body

        response = await call_next(request)
        process_time = time.time() - start_time

        # Only log mutating API requests
        if request.url.path.startswith("/api/") and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if project_id_str:
                db: Session = SessionLocal()
                try:
                    proj_id = UUID(project_id_str)
                    
                    # If auth middleware or deps populated user on state, use it. Otherwise use demo user.
                    user_id = getattr(request.state, "user", DEFAULT_DEMO_USER_ID)
                    if hasattr(user_id, "id"):
                        user_id = user_id.id

                    event = AuditEvent(
                        project_id=proj_id,
                        event_type=f"{request.method} {request.url.path}",
                        actor_id=user_id,
                        payload={
                            "status_code": response.status_code,
                            "process_time_ms": int(process_time * 1000)
                        }
                    )
                    db.add(event)
                    db.commit()
                except Exception as e:
                    logger.error(f"Failed to write audit log: {e}")
                finally:
                    db.close()

        return response
