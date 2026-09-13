# Architecture Decisions

## Decision 1 — Preserve the working bounded workflow

The repository already contains a verified local Resume/JD workflow. That workflow is treated as the core vertical slice and must remain runnable while higher-order capabilities are added.

### Rationale

- It proves the control-plane and validation pattern.
- It is suitable for local testing and demo execution.
- It avoids a risky full rewrite.

## Decision 2 — Keep the API runtime local and explicit

The current API uses a local SQLite runtime store and server-side in-memory collections for user/project/mission coordination. This is intentionally bounded and safe for local development but not durable multi-user production storage.

### Rationale

- Keeps the current slice runnable with minimal dependencies.
- Avoids creating a fake deployment architecture.
- Preserves a migration path to PostgreSQL and repository services.

## Decision 3 — Authentication is intentionally minimal but real for the current slice

The current app includes registration, login, bearer-token verification, and project access checks. The model is intentionally simpler than the full recommended architecture but is a concrete step toward server-side identity enforcement.

### Constraints

- Demo compatibility is retained to avoid breaking existing local usage.
- Real authenticated access is enforced for project-scoped APIs.
- The code should not be mistaken for a full enterprise identity service.

## Decision 4 — Policy and strategy remain central

The policy and strategy modules are treated as control-plane components, not model outputs. They are intended to decide what is allowed before execution proceeds.

### Rationale

- Keeps governance centralized.
- Avoids frontend-driven execution authority.
- Preserves transparency and explainability.

## Decision 5 — Model/tool/provider layers remain future architecture

The repository does not yet implement a provider abstraction, tool registry, or model gateway. Those are treated as future capabilities until the bounded V1 slice is verified end-to-end and durable.

### Rationale

- Prevents false claims of full AI orchestration capability.
- Keeps the codebase maintainable.
- Supports incremental implementation without architectural drift.

## Decision 6 — Frontend is presentation-only, not orchestration authority

The frontend is allowed to call backend APIs and render data, but it must not decide policy outcomes or mission completion.

### Rationale

- Matches the VOID principle.
- Preserves centralized execution authority.
- Reduces attack surface and bypass risk.

## Decision 7 — Requirements must be test-backed before claimed complete

Any feature marked as implemented must be backed by code and relevant tests or executed validation.

### Rationale

- Prevents documentation drift.
- Preserves trust in the project state.
- Aligns with the spec’s requirement to avoid fake implementation claims.
