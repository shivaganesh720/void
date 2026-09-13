# VOID Release Candidate Checklist

**Date:** 2026-09-13  
**Commit:** `9e7bb02` (`updated`)  
**Branch:** `main`

## Repository hygiene

- One pre-existing modified file was present at inspection start: `frontend/next-env.d.ts`.
- No untracked files, tracked secrets, database files, logs, build artifacts, or large binary files were found by the release inspection.
- `.env` is ignored. `.env.example` contains names and development-safe placeholder values only.
- `.venv`, `.pytest_cache`, `__pycache__`, and frontend build output are local/generated and ignored.
- No files were deleted automatically.

## Required environment

| Variable                   | Required now         | Meaning                                                   |
| -------------------------- | -------------------- | --------------------------------------------------------- |
| `ENVIRONMENT`              | No                   | Defaults to `development`.                                |
| `DATABASE_URL`             | No for current slice | Reserved for future authenticated PostgreSQL persistence. |
| `RUNTIME_DB_PATH`          | No                   | Local SQLite path; defaults to `.local/void.sqlite3`.     |
| `MAX_UPLOAD_BYTES`         | No                   | Defaults to 10 MiB.                                       |
| `ALLOWED_ORIGINS`          | No                   | Defaults to `http://localhost:3000`.                      |
| `NEXT_PUBLIC_API_BASE_URL` | No                   | Frontend API target; defaults to `http://127.0.0.1:8000`. |

No AI provider key is required. The analyzer is deterministic and local.

## Required services and setup

- Python virtual environment with `backend/requirements.txt` installed.
- Node.js/npm with `frontend` dependencies installed.
- PostgreSQL is not required for this slice and has no runtime startup path.
- No worker, scheduler, WebSocket, authentication service, or external model provider exists.
- The local runtime applies an idempotent SQLite schema and persists missions; PostgreSQL sessions and a migration runner are not connected.

## Startup commands

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In a second PowerShell window:

```powershell
Set-Location frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

## Verification

- Backend: `16 passed` with two dependency deprecation warnings.
- Frontend: `npm run build` passed.
- API smoke: health/readiness `200`, mission create `201`, detail/list `200`, invalid upload `422`.
- Cross-project lookup returned `404` under the development project filter.

## Known limitations and blockers

Authentication and server-derived project membership are missing. Local mission/task/event/result state persists in SQLite but is not a tenant boundary. There is no PostgreSQL repository, worker, queue, retry, cancellation, approval, artifact, provider, or browser E2E layer. `npm run lint` remains unavailable because the script uses unsupported `next lint` behavior for this installed Next.js version.

**Release candidate classification:** suitable for a controlled local portfolio demonstration only; not a production release.
