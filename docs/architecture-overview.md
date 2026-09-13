# VOID Architecture Overview

## Implemented slice

The current runtime is a two-process local presentation and API system. Next.js renders a single hash-navigated client shell. FastAPI owns request validation, CORS, typed responses, upload parsing, synchronous mission execution, lifecycle validation, and safe server logging. A process-local dictionary stores missions, tasks, results, and events.

The Resume/JD workflow validates supported inputs, extracts text, builds and validates structured analysis, performs deterministic lexical skill comparison, and records terminal mission/task state. SQLAlchemy classes describe future entities but have no engine, session, migration, repository, or runtime query wiring.

## Intended but not connected

The target architecture includes authenticated application boundaries, a VMCF control plane, work graph, scheduler/worker, model/tool/agent gateways, approvals, artifacts, audit persistence, and PostgreSQL. Those boundaries are documented as design direction, not current capabilities.

## Classification

- **Implemented:** health endpoints, contracts, lifecycle validation, bounded parsing/validation, deterministic Resume/JD analysis, in-memory mission observability, frontend build.
- **Partially implemented:** dashboard, mission detail/timeline, policy/strategy helpers, CORS, SQLAlchemy model definitions.
- **Not implemented:** authentication, authorization, persistence, migrations, workers, gateways, approvals, artifacts, settings, retries, cancellation, audit persistence, browser E2E.
- **Not verified:** production concurrency, deployment, browser performance, database behavior, external providers.

## Invariants

The frontend does not select models or tools. Current execution uses no external model or tool. Untrusted document content is parsed and validated before analysis. Client project IDs are development filters only and must not be treated as authorization.
