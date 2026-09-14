# File Cleanup Manifest

| Original Path | Action | New Path | Reason | Verified |
|---------------|--------|----------|--------|----------|
| `backend/app/routers/` | MOVED | `apps/backend/app/api/v1/` | Enforce API separation from core logic | YES |
| `backend/app/control_plane/policy.py` | MOVED | `apps/backend/app/policies/evaluator.py` | Isolate policy engine from API routes | YES |
| `backend/app/gateways/` | MOVED | `apps/backend/app/integrations/` | Centralize 3rd party providers/tools | YES |
| `backend/app/workflows/resume_jd.py` | MOVED | `apps/backend/app/capabilities/resume_jd/` | Module domain logic | YES |
| `backend/app/db/base.py` | MOVED | `apps/backend/app/models/base.py` | Centralize DB schemas as models | YES |
| `frontend/app/` | MOVED | `apps/frontend/src/app/` | Feature-based architectural layout | YES |
| `docs/API.md` | MOVED | `docs/api/API.md` | Clean structure for documentation | YES |
| `backend/__pycache__/` | DELETED | — | Unused and safe to remove | YES |
