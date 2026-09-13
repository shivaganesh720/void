# VOID Runtime Services

## Current development runtime

Required:

- FastAPI/Uvicorn backend on port 8000.
- Next.js frontend on port 3000.

Not required by the current slice:

- PostgreSQL: SQLAlchemy models exist, but no runtime session is connected.
- Redis/RabbitMQ: no queue or worker exists.
- Model provider: the Resume/JD analyzer is deterministic and local.
- WebSocket service: the frontend uses HTTP polling for an active mission.

## Startup

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In another shell:

```powershell
Set-Location frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```
