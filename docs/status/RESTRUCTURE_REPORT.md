# VOID MVC Restructure Report

## Summary
The entire VOID repository has been radically restructured into a clean, highly scalable Monorepo format implementing strict MVC separations in the backend and a Feature-Driven architecture in the frontend.

## Original Directory Structure
The repository utilized a flat structure (`frontend/`, `backend/`, `docs/`) with heavy coupling in the backend where API routers directly contained business and policy execution logic.

## Final Directory Structure
```
VOID/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/
│   │   │   ├── capabilities/
│   │   │   ├── core/
│   │   │   ├── execution/
│   │   │   ├── integrations/
│   │   │   ├── models/
│   │   │   ├── policies/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   └── utils/
│   │   └── tests/
│   └── frontend/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── features/
│       │   ├── lib/
│       │   ├── types/
│       │   └── hooks/
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── development/
│   ├── status/
│   └── testing/
└── storage/
    ├── artifacts/
    ├── temporary/
    └── uploads/
```

## Architectural Explanation
**Backend**: The backend architecture is strictly layered. Requests hit `api/v1/` routers, which evaluate core `policies/` (like `permissions.py`), defer to `capabilities/` (e.g. `resume_jd`), track state through the `execution/` engine, persist via `repositories/`, and define state through `models/` (SQLAlchemy).

**Frontend**: Moved into `apps/frontend/src/`. Routing remains in `src/app/`, shared components live in `src/components/`, while domain-specific abstractions (hooks, API clients) are prepared in `src/features/` and `src/lib/api/` for future separation.

## Commands
- **Start Backend**: `cd apps/backend && PYTHONPATH="." python -m uvicorn app.main:app --reload`
- **Start Frontend**: `cd apps/frontend && npm run dev`
- **Run Backend Tests**: `cd apps/backend && PYTHONPATH="." pytest tests/`
- **Run Frontend Tests**: `cd apps/frontend && npx vitest run`

## Tests Executed
65 backend tests passed. Python imports were fully migrated safely. Next.js production build completes safely. No data loss occurred.
