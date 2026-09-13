# VOID Architecture

## Purpose

VOID is a governed control and execution plane. The frontend collects intent and displays state. The backend validates requests, resolves strategy, applies policy, executes bounded work, validates results, and persists evidence and audit data.

## Request flow

```text
User
  -> Presentation
  -> Application API
  -> Intent Gate
  -> Mission Kernel
  -> Execution Profile
  -> Capability Broker
  -> Strategy Resolver
  -> Pre-Execution Policy
  -> Mission Blueprint
  -> Work Graph
  -> Task State Service
  -> Agent Harness / Tool Gateway / Model Gateway
  -> Validation
  -> Artifact and Audit Persistence
```

## Boundaries

### Presentation

Displays missions, tasks, approvals, evidence, artifacts, and errors. It does not select models, authorize tools, orchestrate tasks, or override policy.

### Application API

Owns authentication, request validation, authorization, project scoping, response contracts, correlation IDs, and error mapping.

### VMCF control plane

Owns intent normalization, execution profile freezing, capability selection, deterministic strategy resolution, policy decisions, approvals, and mission control.

### Execution fabric

Owns work graphs, scheduling, task state, attempts, leases, cancellation, retries, agent cells, context building, gateways, result merging, and execution receipts.

### Persistence

Stores project-scoped missions, inputs, profiles, blueprints, tasks, attempts, decisions, approvals, artifacts, evidence, usage, errors, and audit events in PostgreSQL.

## Invariants

1. The frontend never orchestrates execution.
2. Agents never call models or tools directly.
3. Every tool call passes through the Tool Gateway.
4. Every model call passes through the Model Gateway.
5. Capability does not imply permission.
6. Model and document content is untrusted until validated.
7. Execution, retries, cost, and time are bounded.
8. Project-scoped data cannot cross project boundaries.
9. Important decisions and state changes are auditable.
10. Human authority is above agent authority.

## Current implementation

Implemented: contracts, lifecycle validation, basic policy and strategy services, upload checks, initial SQLAlchemy models, health endpoints, and a frontend shell.

Not implemented: authentication, migrations, mission APIs, real document extraction, gateways, scheduler, approvals, artifacts, audit persistence, and end-to-end execution.
