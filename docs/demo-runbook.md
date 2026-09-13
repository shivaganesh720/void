# VOID Demo Runbook

## Prerequisites

Windows PowerShell, Python 3.x, Node.js/npm, and the repository checkout. No PostgreSQL, API key, worker, or external AI provider is needed.

## Install and configure

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Set-Location frontend
npm install
Set-Location ..
Copy-Item .env.example .env
```

The template is safe for local use. `DATABASE_URL` is not consumed by the current runtime.

## Start

PowerShell 1:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

PowerShell 2:

```powershell
Set-Location frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

Open `http://localhost:3000`. Confirm `http://127.0.0.1:8000/health/ready` returns `{"status":"ok",...}`.

## Demo flow

1. On Dashboard, paste synthetic resume text such as `Python FastAPI SQLAlchemy testing`.
2. Paste synthetic job text such as `Need Python FastAPI and testing skills`.
3. Select **Start analysis**.
4. Show the completed status, match score, matching/missing skills, defects, action plan, and evidence.
5. Open **Missions**, refresh, and open the mission row.
6. Show task status, execution mode, completion time, and lifecycle timeline.
7. Visit Approvals, Artifacts, and Settings to show their explicit unavailable states.
8. Optionally repeat with two synthetic `.txt` files to demonstrate upload validation.

No IDs need to be copied, no database edits are required, and no mock response is used. The UI currently uses the documented development project context.

## Expected output

A mission completes synchronously with `COMPLETED` mission/task state and a deterministic lexical analysis. Data is retained only until the backend process restarts.

## Common errors and recovery

- API unavailable: start the backend first and confirm `/health/ready`.
- Frontend targets the wrong API: set `NEXT_PUBLIC_API_BASE_URL` before `npm run dev`.
- Mixed file/text input: provide both files or both text fields.
- Invalid/empty/unsupported file: use readable PDF, DOCX, TXT, or Markdown with text.
- No missions after restart: expected; the store is in memory. Run the demo again.

## Cleanup

Stop both terminals with `Ctrl+C`. Delete only the local `.env` if it was created for the demo. Do not reset or delete any database; the current slice does not create one. Synthetic inputs can be discarded immediately.
