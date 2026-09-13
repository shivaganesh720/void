# VOID Development Guide

## Local loop

From the repository root, use the project virtual environment and set `PYTHONPATH=backend` for backend commands. Install backend dependencies from `backend/requirements.txt`; install frontend dependencies from `frontend/package.json`.

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest tests\unit -q
Set-Location frontend
npm run build
npm audit
```

Run the API with Uvicorn and the UI with `npm run dev` as described in [demo-runbook.md](demo-runbook.md).

## Change boundaries

Keep the frontend presentation-only. Keep mission transitions centralized in the lifecycle validator. Validate untrusted files before parsing and validate structured analysis before returning or storing it. Never treat client-supplied project IDs as authorization. Update the relevant status and release reports when behavior changes.

## Testing expectations

Current tests cover contracts, health, policy/strategy helpers, file validation/parsing, mission lifecycle, filtering, and Resume/JD analysis. Missing coverage includes authentication, durable isolation, migrations, retries, cancellation, providers, settings, approvals, artifacts, and browser E2E. Do not report a coverage percentage without a coverage measurement.

## Known tooling note

The current `frontend` lint script invokes `next lint`, which is unsupported by the installed Next.js release. The production build and TypeScript checks pass; repair the lint command as a separate tooling task before treating lint as a release gate.
