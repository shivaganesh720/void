# VOID Development Rules

## Working cycle

```text
Implement -> Run -> Test -> Inspect -> Fix -> Document
```

The repository is the source of truth. Never mark a feature complete from code inspection alone.

## Before editing

1. Read `BUILD_STATUS.md`.
2. Read the relevant architecture and security documents.
3. Check `git status`.
4. Inspect nearby code and tests.
5. Identify the smallest testable change.

## Engineering rules

- Keep controllers thin and put business logic in services.
- Use typed contracts and explicit status values.
- Keep provider-specific code behind adapters.
- Use PostgreSQL migrations for schema changes.
- Keep secrets in environment configuration, never source code.
- Do not add fake providers, fake progress, or fake mission results.
- Bound retries, loops, costs, time, tokens, and file sizes.
- Preserve project isolation on every project-scoped query.
- Do not introduce Docker or distributed infrastructure unless required by a later verified milestone.

## Required validation

From the repository root:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest tests\unit -q
Set-Location frontend
npm run build
npm audit
```

A feature may be labelled VERIFIED only with executable test evidence. Document known warnings and limitations.

## Current validation result

As of 2026-09-13: 15 backend unit tests pass, the frontend build passes, npm reports zero vulnerabilities, and backend health/readiness/OpenAPI checks return 200 when Uvicorn is running. Two test-client deprecation warnings remain.
