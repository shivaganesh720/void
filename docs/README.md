# VOID Documentation

This directory contains the canonical documentation for the current VOID implementation.

## Start here

- [V1 scope](V1_SCOPE.md) - product boundaries and non-goals
- [Requirement status](REQUIREMENT_STATUS.md) - implemented, partial, deferred, and blocked requirements
- [Implementation plan](IMPLEMENTATION_PLAN.md) - ordered work phases
- [Architecture decisions](ARCHITECTURE_DECISIONS.md) - decisions that govern the local implementation
- [Security model](security-model.md) - security boundaries and known limitations
- [API reference](void-api-reference.md) - available backend endpoints
- [End-to-end workflow](end-to-end-workflow.md) - current user and mission flow
- [Demo runbook](demo-runbook.md) - local setup and demonstration steps

## Source-of-truth rules

The code and tests are authoritative for implemented behavior. The status register must not claim a feature is complete without executable evidence. Historical audit reports and duplicated status snapshots are intentionally not maintained here.

## Current product state

VOID is a runnable local Resume/JD intelligence workflow with a public landing page, registration, login, onboarding, project-scoped workspace, mission execution, evidence, and explanation reporting. PostgreSQL persistence, refresh-token rotation, email delivery, durable files, gateways, workers, and full browser E2E coverage remain future work.
