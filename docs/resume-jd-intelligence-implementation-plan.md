# Resume/JD Intelligence Implementation Plan

## Existing surface

- `backend/app/main.py` owns the FastAPI boundary, in-memory mission store, lifecycle transitions, and retrieval.
- `backend/app/control_plane/{policy,state,strategy}.py` owns deterministic governance and state validation.
- `backend/app/files/validation.py` validates upload names, sizes, extensions, and executable content.
- `backend/app/files/parsing.py` now extracts UTF-8 text, DOCX XML text, and PDF text through the optional `pypdf` gateway.
- `backend/app/workflows/resume_jd_analysis.py` produces and validates the structured evidence-backed result.
- `frontend/app/page.tsx` renders mission status, file inputs, score, gaps, defects, evidence, and action plan.

## Gaps and connections

The repository has no authentication middleware, database session wiring, scheduler, model gateway, agent cells, or durable mission persistence. The current implementation keeps the existing governed in-memory executor and adds explicit parsing and validation boundaries; it does not pretend those missing production components exist.

## Workflow

Upload -> Parse -> Mission Creation -> governed lifecycle -> bounded analysis -> validation -> in-memory persistence -> structured UI result.

## Expected future changes

Add authenticated project context, durable file/artifact storage, a scheduler/work graph with one task record per stage, a provider-neutral Model Gateway, retry persistence, and migrations before production use.

## Test plan

Run backend unit tests, parser tests, upload endpoint tests, malformed/empty/oversized input checks, and frontend production type/build checks. Verify provider absence is surfaced as a limitation and never represented as an external model call.
