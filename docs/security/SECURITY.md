# VOID Security Model & Rules

## 1. Threat Model
- **Untrusted Input:** All prompt content, uploaded documents, and LLM generated outputs are treated as untrusted. They must be validated before persistence or execution.
- **Agent Containment:** Agents run within strict capability boundaries. They cannot access the filesystem directly, execute raw terminal commands, or bypass the `SafeToolGateway`.
- **Project Isolation:** Data leakage between projects is prevented at the database layer. All queries for missions, tasks, and artifacts must include a `project_id` filter.

## 2. Authentication & Authorization
- **Authentication:** Standard JWT (Bearer Tokens) are required for all protected endpoints.
- **Authorization:** Handled via FastAPI dependencies. 
  - `get_current_user` extracts identity.
  - Role-based Access Control (RBAC) allows only `ADMIN` roles to access `/api/v1/admin/*` endpoints.

## 3. Auditing & Governance
- **Audit Middleware:** All mutating requests (POST, PATCH, PUT, DELETE) are automatically intercepted and logged as `AuditEvent` records in the database.
- **Approvals:** High-risk actions require manual human approval via the `/api/v1/approvals` router. Agents pause execution until the approval is granted.

## 4. Coding Rules
1. **Never use raw SQL:** Always use SQLAlchemy ORM or the query builder to prevent SQL injection.
2. **Never hardcode secrets:** All configuration MUST be loaded from environment variables via `app.core.config.Settings`.
3. **Always validate schema:** Use Pydantic models for all API requests and responses.
4. **Assume compromise:** Write every tool as if the agent calling it is actively trying to bypass boundaries.
