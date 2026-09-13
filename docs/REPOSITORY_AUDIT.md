# VOID Repository Audit

**Audit date:** 2026-09-13  
**Repository state:** Existing local implementation, partially complete

## Current architecture

- `backend/app/main.py` exposes the FastAPI application, authentication flow, project access checks, mission APIs, approvals, dashboard data, and the synchronous Resume/JD execution path.
- `backend/app/contracts` contains typed request/response contracts and lifecycle enums.
- `backend/app/control_plane` contains lifecycle transition validation, deterministic policy evaluation, and deterministic strategy selection.
- `backend/app/files` validates and parses bounded PDF, DOCX, text, and Markdown inputs.
- `backend/app/workflows` contains the deterministic Resume/JD analyzer and structured result validation.
- `backend/app/db/base.py` defines initial SQLAlchemy entities; `backend/app/db/session.py` provides engine/session helpers; `backend/app/db/runtime.py` provides a small SQLite mission payload store.
- `frontend/app` is a Next.js presentation shell for public authentication/onboarding and the protected workspace. It reads backend data and does not own orchestration.

## Working components

- FastAPI liveness/readiness and OpenAPI endpoints.
- Registration, login, bearer-token verification, profile update, logout response, onboarding project creation, and project membership checks.
- Project-scoped mission list/detail/task/event/dashboard reads.
- Resume/JD text and file intake with upload size, extension, filename, and executable-content checks.
- Bounded document parsing and deterministic lexical Resume/JD analysis with structured validation, warnings, defects, recommendations, and source-labelled evidence.
- Lifecycle transition validation and deterministic policy/strategy helpers.
- SQLAlchemy model definitions for users, projects, project members, missions, tasks, artifacts, and audit events.
- Next.js routes for public auth flows and the protected workspace, including truthful unavailable states for features not yet backed by APIs.

## Partially implemented components

- `RuntimeStore` persists mission payloads in SQLite, but the primary API state is still held in process-memory dictionaries.
- SQLAlchemy session helpers initialize metadata but are not wired into request handling or repositories.
- Auth is real for the local slice but tokens and identity are not durable sessions with rotation or revocation.
- Mission execution is synchronous and bounded locally; there is no durable worker, lease, retry, timeout, or cancellation service.
- Domain models include artifact and audit foundations, but no durable artifact/audit API or execution receipt is integrated.
- Frontend mission display is connected to the existing mission APIs, while approvals, artifacts, evidence, memory, and broader control-plane screens remain unavailable or future-facing.

## Missing V1 components

- Migration-driven durable PostgreSQL repositories and project isolation at the persistence layer.
- Durable users, sessions, projects, missions, tasks, approvals, artifacts, evidence, and audit events.
- Model Gateway, Tool Gateway, Agent Harness, registered agents, scheduler, work graph, cancellation, and bounded recovery.
- Research and Learning workflows at an executable, evidence-backed level.
- Real artifact receipts/versioning, evidence ledger, cost/privacy accounting, execution transparency records, and integration/browser tests.

## Reusable code and boundaries

- Preserve the existing Resume/JD workflow as the first vertical slice; its parser, analyzer, validator, contracts, lifecycle events, and frontend rendering are the strongest working foundation.
- Keep policy and strategy decisions in `control_plane` rather than moving them into the frontend or model layer.
- Reuse the existing error contracts, settings, SQLAlchemy entities, and runtime persistence boundary when adding repositories.
- Keep external model providers, tools, and future background execution behind explicit gateway/service interfaces. Do not add fake providers or fake progress.

## Risks

- Process-memory state can disappear on restart and cannot provide production-grade multi-user isolation.
- The current fallback authentication behavior is intentionally demo-compatible and must not be presented as production identity management.
- No migration runner is wired to the runtime, so SQLAlchemy metadata is not a deployable schema contract yet.
- The synchronous API path has no durable cancellation or retry boundary.
- The analyzer is lexical and explicitly cannot verify visual formatting, factual truth, or external evidence.

## Verified commands and current evidence

- Backend unit suite: `PYTHONPATH=backend .venv/Scripts/python.exe -m pytest tests/unit -q` is documented as passing 21 tests.
- Frontend production build: `npm run build` in `frontend` is documented as passing on Next.js 16.3.5.
- Frontend dependency audit: `npm audit` is documented as reporting zero vulnerabilities.
- Database migrations and end-to-end mission execution are documented as not implemented.
- `rg` is not available in the current PowerShell environment; repository searches use the available VS Code/workspace tools instead.

## Proposed implementation order

1. Wire the existing SQLAlchemy foundation behind a small repository boundary, starting with users/projects and an explicit local SQLite test path.
2. Add migration configuration and an initial migration without changing the verified in-memory demo behavior until repository tests are green.
3. Move mission/task/event persistence behind the same boundary and add restart/isolation tests.
4. Add approvals, artifact receipts, and audit persistence using the existing contracts and model boundaries.
5. Introduce execution services and gateways only when each has a real provider/tool contract and focused tests.
6. Integrate frontend screens only against real APIs, then add integration/browser coverage and update status documents.

## Cleanup recommendations

- Do not remove the existing local runtime store or demo compatibility until the durable replacement has equivalent tests.
- Keep generated `.local`, cache, and virtual-environment content out of source changes.
- Consolidate status claims through `BUILD_STATUS.md`, this audit, and the existing requirement/security reports rather than creating duplicate planning documents.
- Treat disabled OCR, RAG/web search, browser automation, arbitrary code execution, and external side effects as disabled until their gateways and policies are executable and tested.
