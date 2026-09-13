# VOID

Versatile Orchestrated Intelligent Dispatcher.

VOID is a governed execution system. It converts human intent into controlled work while keeping policy, permissions, validation, evidence, and auditability outside the authority of models and agents.

## Current status

- Phase: contracts and initial foundation
- Completion: partial, approximately 15%
- Backend tests: 9 passing
- Frontend build: passing
- Frontend dependency audit: 0 vulnerabilities
- Production readiness: not yet claimed

Implemented now:

- FastAPI liveness and readiness endpoints
- Typed execution modes, mission states, task states, policy decisions, and API schemas
- Central lifecycle transition validation
- Deterministic policy and Resume/JD strategy services
- Basic safe upload validation
- Lexical Resume/JD skill comparison with source-labelled evidence
- PostgreSQL-ready SQLAlchemy models
- Next.js mission-control presentation shell

Not implemented yet:

- Authentication and project authorization
- Database sessions and Alembic migrations
- Mission and file APIs
- PDF/DOCX extraction
- Model Gateway, Tool Gateway, Agent Harness, scheduler, approvals, artifacts, and audit persistence
- End-to-end mission execution

The development Resume/JD text slice is now executable through `POST /api/v1/missions/resume-jd` and retrievable through `GET /api/v1/missions/{mission_id}`. It is synchronous, in-memory, and lexical-only; it does not provide durable persistence or model-backed execution. See [docs/runtime-execution-debug-report.md](docs/runtime-execution-debug-report.md).

## Requirements

- Windows PowerShell
- Python 3.14 or compatible Python 3.x
- Node.js and npm
- PostgreSQL is optional for the current health and unit-test slice

## Backend commands

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest tests\unit -q
```

Start the backend:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000/health/live
- http://127.0.0.1:8000/health/ready
- http://127.0.0.1:8000/docs

## Frontend commands

```powershell
Set-Location frontend
npm install
npm run dev
```

Open http://localhost:3000.

Verify the production bundle and dependencies:

```powershell
npm run build
npm audit
```

## Repository map

```text
backend/app/       FastAPI application and domain services
tests/unit/        Backend unit tests
frontend/          Next.js presentation shell
docs/              Audits, progress, reports, and security notes
.env.example       Environment variable template
```

## Documentation

- [BUILD_STATUS.md](BUILD_STATUS.md): current verified state
- [ARCHITECTURE.md](ARCHITECTURE.md): system boundaries and invariants
- [VOID_SPEC.md](VOID_SPEC.md): target requirements and non-goals
- [SECURITY_RULES.md](SECURITY_RULES.md): security rules
- [docs/implementation-audit.md](docs/implementation-audit.md): repository audit
- [docs/final-implementation-report.md](docs/final-implementation-report.md): current report

## Important rule

Code is not complete merely because it exists. A feature is complete only when it is executable, tested, documented, and compliant with the governance and security rules.
