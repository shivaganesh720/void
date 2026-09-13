# VOID V1 Implementation Plan

## Phase checklist

### Phase 0 — Scope freeze and status register

- [x] Create V1 scope statement
- [x] Create requirement status register
- [x] Document implementation plan
- [x] Document architecture decisions

### Phase 1 — Repository and development foundation

- [x] Verify existing repo structure
- [x] Keep existing bounded backend flow intact
- [x] Establish app and frontend foundation
- [x] Keep health-check and local dev startup runnable
- [ ] Add stricter multi-user deployment environment separation

### Phase 2 — Shared contracts and domain models

- [x] Extend contracts for auth, project, execution profiles, and reports
- [x] Keep contract naming consistent with backend runtime
- [ ] Add a durable domain model layer for full user/admin objects

### Phase 3 — Multi-user authentication and authorization

- [x] Add basic registration/login endpoints
- [x] Add token-based auth flow for local demo usage
- [x] Add project access enforcement for authenticated requests
- [x] Add current-user, logout, and onboarding profile endpoints
- [x] Upgrade local password storage to salted PBKDF2 verification
- [ ] Add refresh-token rotation and revocation
- [ ] Add durable user/session tracking
- [ ] Add admin role enforcement and full ownership checks for all entities

### Phase 4 — User AI experience profile

- [x] Add explicit local runtime user profile fields
- [x] Add onboarding flow models
- [x] Add AI-aware vs AI-unaware mode handling

### Phase 5 — Project, session, mission management

- [x] Create project and mission flow for local slice
- [x] Persist mission runtime state with local SQLite
- [ ] Add durable session layer
- [ ] Add full mission lifecycle transitions including recover/cancel/paused states

### Phase 6 — Secure file upload and document processing

- [x] Add file validation and parsing
- [x] Support PDF/DOCX/TXT/MD bounded analysis
- [ ] Add secure durable storage with ownership and retention
- [ ] Add scanned-PDF rejection and stricter extraction diagnostics

### Phase 7 — Intent Gate

- [x] Capture mission intent in API
- [ ] Formalize full intent classification model
- [ ] Persist structured intent separately for each mission

### Phase 8 — Mission Kernel and execution profile

- [x] Add execution profile model support
- [ ] Add full immutably-snapshotted mission blueprint and config hash

### Phase 9 — AUTO/GUIDED/MANUAL modes

- [x] Mode values recognized in the contracts
- [ ] Fully implement guided/manual orchestration with review and approval states

### Phase 10 — Capability registry

- [ ] Add capability registry and status metadata

### Phase 11 — Strategy Resolver

- [ ] Add strategy selection service connected to mission inputs

### Phase 12 — TaskState, work graph, execution fabric

- [x] Validate task state transitions
- [ ] Add full durable task graph and retries/cancellation

### Phase 13 — Agent cells and harness

- [ ] Add agent registry and execution harness

### Phase 14 — Model gateway

- [ ] Add provider-agnostic gateway and isolation layer

### Phase 15 — Tool gateway

- [ ] Add tool registry, allowlists, and policy enforcement

### Phase 16 — Resume/JD intelligence pipeline

- [x] Implement parser + analysis + recommendations -> result flows
- [x] Add explanation report generation
- [ ] Add richer artifact versioning and protected outputs

### Phase 17 — Result merge and validation

- [x] Add structured validation before returning results
- [ ] Add deeper semantic policy checks and durable evidence provenance

### Phase 18 — Governance and policy engine

- [x] Basic policy decision helpers exist
- [ ] Enforce policy centrally in all risky runtime calls

### Phase 19 — Approval workflow

- [ ] Add full approval records and resumption logic

### Phase 20 — Execution Learning Report

- [x] Generate a local execution summary report for mission results
- [ ] Expand report to richer versioned, evidence-backed outputs

### Phase 21 — Artifacts, evidence, and retention

- [ ] Add durable artifact registry and retention system

### Phase 22 — Premium light UI implementation

- [x] Replace the minimal UI with a light premium dashboard shell
- [x] Add public landing, registration, login, onboarding, and workspace screens
- [x] Add recovery and verification route placeholders with truthful local limitations

### Phase 23 — Admin interface

- [ ] Add admin-only backends and frontend screens

### Phase 24 — Observability and ops

- [ ] Add full structured logging, metrics, and runbook

### Phase 25 — Error handling and recovery

- [ ] Add full error taxonomy, retries, and mission recovery flow

### Phase 26 — Testing and QA

- [x] Add functioning backend tests for auth/profile, runtime store, workflow, files, and health
- [ ] Add full integration, E2E, and security coverage

### Phase 27 — Hybrid deployment

- [ ] Add durable deployment and local multi-user environment configuration

### Phase 28 — Final V1 completion gate

- [ ] Complete and verify all V1 acceptance checks

## Execution note

The current implementation is stable enough to remain runnable while the missing higher-order capabilities are documented and planned. This approach avoids breaking the working bounded workflow while preserving a clear roadmap.
