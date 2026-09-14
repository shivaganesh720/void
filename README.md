# VOID
**Versatile Orchestrated Intelligent Dispatcher**: a governed local execution prototype with a bounded Resume/JD analysis workflow.

## Status
VOID is structured as an enterprise-grade MVC monorepo (`apps/backend` and `apps/frontend`). It delivers a governed product journey from public landing page through registration, onboarding, project-scoped workspace, and deterministic Resume/JD analysis.

## Key Features
- **MVC Backend**: Clean architectural boundaries across `api`, `controllers`, `services`, `repositories`, and `models`.
- **Feature-Driven Frontend**: Next.js 16 UI structured strictly by feature modules inside `src/`.
- **Hardened Security**: Protected endpoints, safe file uploads, and project-isolated tenant boundaries.

## Installation and Environment

Windows PowerShell is the verified local path. From the repository root:

```powershell
# 1. Setup Virtual Environment & Backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps\backend\requirements.txt
Copy-Item .env.example .env

# 2. Setup Frontend
Set-Location apps\frontend
npm install
Set-Location ..\..
```

## Run and Test

### Start the Backend Server

```powershell
$env:PYTHONPATH = "apps\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps\backend --host 127.0.0.1 --port 8000 --reload
```

### Start the Frontend Server
In a separate PowerShell window:

```powershell
Set-Location apps\frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

Open `http://localhost:3000` to view the VOID application.

### Run Tests

Backend Tests:
```powershell
Set-Location apps\backend
$env:PYTHONPATH = "."
..\..\.venv\Scripts\python.exe -m pytest tests/
```

Frontend Build & Tests:
```powershell
Set-Location apps\frontend
npx vitest run
npm run build
```

## Project Structure

```
VOID/
├── apps/
│   ├── backend/          # FastAPI MVC application
│   └── frontend/         # Next.js 16 Feature-driven application
├── docs/                 # Architectural and security documentation
└── storage/              # Git-ignored local development payloads
```

See [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) and [docs/status/RESTRUCTURE_REPORT.md](docs/status/RESTRUCTURE_REPORT.md) for deeper technical overviews of the implementation.
