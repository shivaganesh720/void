# VOID Runtime Startup Report

**Date:** 2026-09-13

## Services

| Service          | Command                                                                                                      | Port | Result                                           |
| ---------------- | ------------------------------------------------------------------------------------------------------------ | ---: | ------------------------------------------------ |
| FastAPI/Uvicorn  | `$env:PYTHONPATH="backend"; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | 8000 | Started successfully                             |
| Next.js          | `Set-Location frontend; npm run dev`                                                                         | 3000 | Command available; not started during this audit |
| PostgreSQL       | No repository startup command                                                                                | 5432 | Not required by current in-memory slice          |
| Worker/scheduler | None exists                                                                                                  |  N/A | Not implemented                                  |
| WebSocket        | None exists                                                                                                  |  N/A | Not implemented                                  |

## Health checks

- `GET http://127.0.0.1:8000/health/live`: 200.
- `GET http://127.0.0.1:8000/health/ready`: 200.
- `GET http://127.0.0.1:8000/openapi.json`: 200.
- Backend startup emitted no application exception.

## Configuration

- `DATABASE_URL` is defined but not consumed by runtime persistence.
- `MAX_UPLOAD_BYTES` configures upload limits.
- `ALLOWED_ORIGINS` configures CORS.
- `NEXT_PUBLIC_API_BASE_URL` configures the frontend API target.
- No model API key or provider is required by the deterministic local analyzer.

## Startup limitations

The first health check failed only because no backend process was listening. After starting Uvicorn, all health checks passed. No database, worker, scheduler, auth, or model services can be verified because they are not implemented.
