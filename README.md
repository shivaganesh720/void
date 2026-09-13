# VOID

**Versatile Orchestrated Intelligent Dispatcher**: a governed local execution prototype with a bounded Resume/JD analysis workflow.

## Status

VOID currently delivers a local governed product journey from public landing page through registration, onboarding, project-scoped workspace, and deterministic Resume/JD analysis. It is suitable for local demonstration and portfolio review, but is not production-ready.

## Problem and solution

Automation systems need policy, validation, evidence, and visible execution state outside model authority. VOID explores that control-plane shape. The implemented slice accepts resume and job-description text or files, validates and parses them, compares skills deterministically, validates structured output, and exposes mission, task, and event state.

## Key features

- FastAPI liveness/readiness and typed API contracts.
- Safe bounded PDF, DOCX, TXT, and Markdown input handling.
- Deterministic skill matching, defects, recommendations, and source-labelled evidence.
- Local SQLite-backed mission, user, and project state for mission list, detail, task, event timeline, filtering, and dashboard summary.
- Next.js interface with loading, empty, error, refresh, and truthful unavailable states.

## Architecture and workflow

The frontend calls the FastAPI boundary. The API validates input, creates a project-scoped mission, runs the synchronous Resume/JD workflow, validates the result, records lifecycle events, and persists the local development payload in SQLite. SQLAlchemy entity definitions still describe a future PostgreSQL repository boundary and are not connected to runtime queries.

1. Open the local dashboard.
2. Paste both documents or upload a supported pair.
3. Start analysis and inspect the completed mission and result.
4. Open Missions to filter and inspect task state and lifecycle events.
5. Refresh or restart to confirm local SQLite state survives the backend process restart; PostgreSQL durability and migration wiring remain deferred.

See [docs/README.md](docs/README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [docs/end-to-end-workflow.md](docs/end-to-end-workflow.md).

## Technology stack

Python 3.x, FastAPI, Pydantic Settings, Uvicorn, SQLAlchemy model definitions, pypdf, pytest, Next.js 16, React 19, TypeScript, and npm.

## Installation and environment

Windows PowerShell is the verified local path. From the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Set-Location frontend
npm install
Set-Location ..
Copy-Item .env.example .env
```

The current runtime reads `ENVIRONMENT`, `DATABASE_URL`, `RUNTIME_DB_PATH`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`, `DB_ECHO`, `MAX_UPLOAD_BYTES`, and `ALLOWED_ORIGINS`. Local missions, users, and projects use the SQLite path in `RUNTIME_DB_PATH` (default `.local/void.sqlite3`), while `DATABASE_URL` can be set to PostgreSQL for durable backend work. The frontend optionally reads `NEXT_PUBLIC_API_BASE_URL` and otherwise uses `http://127.0.0.1:8000`.

## Run and test

Backend:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend, in another PowerShell window:

```powershell
Set-Location frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

Open `http://localhost:3000`. Verify with `$env:PYTHONPATH="backend"; .\.venv\Scripts\python.exe -m pytest tests\unit -q`, `npm run build`, and `npm audit` from `frontend`.

## Demo and screenshots

Follow [docs/demo-runbook.md](docs/demo-runbook.md). No screenshots are committed yet; the runbook identifies the dashboard, completed result, and mission timeline views to capture for a portfolio presentation.

## Security and limitations

Upload validation, output validation, CORS configuration, safe logging, bearer authentication, project membership checks, and local SQLite identity storage are covered in the current slice. Refresh-token rotation, PostgreSQL identity storage, email delivery, and production deployment hardening remain deferred. See [docs/security-model.md](docs/security-model.md) and [docs/REQUIREMENT_STATUS.md](docs/REQUIREMENT_STATUS.md).

## Project structure

`backend/app` contains the API, contracts, control-plane helpers, parsing, and workflow. `frontend` contains the Next.js presentation shell. `tests/unit` contains backend tests. `docs` contains release, architecture, security, testing, and limitation reports.

## Roadmap and contribution

The next release prerequisites are authenticated identity and project membership, database sessions/migrations/repositories, durable mission state, a worker contract, and integration/browser tests. Do not present planned control-plane components as implemented. Contributions should preserve the boundaries in [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) and update the relevant status report.

Author and contribution attribution should be added by the project owner before public publication.
