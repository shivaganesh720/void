# Test Coverage Readiness

## Executed on 2026-09-13

- `PYTHONPATH=backend .venv/Scripts/python.exe -m pytest tests/unit -q`: **15 passed**, 2 dependency deprecation warnings.
- `frontend/npm run build`: **passed**.
- API smoke: health/readiness, create, list, detail, invalid upload, and cross-project mismatch: **passed**.

## Covered

Contracts, health, policy/strategy pure functions, lifecycle transitions, Resume/JD text and upload paths, parsing/validation failures, result validation, mission list/detail/task/event reads, filtering, and dashboard summary.

## Missing or blocked

Authentication, project isolation with real identity, durable database/migrations, deletion and transactions, provider failure/rate limits/timeouts, retries, cancellation, worker crashes, tool permissions, approval persistence, artifact ownership, settings persistence, browser acceptance, accessibility, concurrency, load, and deployment tests.

No coverage percentage is claimed. `npm run lint` is not a valid release check until its existing `next lint` script is updated for the installed Next.js version.
