# VOID Architecture

## System Overview

VOID is a governed control and execution plane for agentic workflows. It ensures that AI agents operate within strict, verifiable boundaries defined by human intent, project scope, and system policies. 

The architecture strictly separates the presentation layer (Frontend) from the control plane (Backend), with a robust relational database (PostgreSQL/SQLite) providing durable persistence.

## Core Components

### 1. Presentation Layer (Frontend)
- **Tech Stack:** Next.js, React, Tailwind CSS.
- **Responsibilities:** Collects user intent, displays mission state, handles authentication flows, and renders real-time streaming updates via WebSockets. It **never** orchestrates execution or makes direct calls to LLMs.

### 2. Application API (Backend)
- **Tech Stack:** FastAPI, Python, SQLAlchemy, Alembic.
- **Responsibilities:** 
  - **Auth & Access:** JWT-based authentication and project-scoped authorization.
  - **Modular Routers:** Clean separation of concerns (`auth`, `missions`, `projects`, `gateways`, `approvals`, `workflows`, `websockets`).
  - **Dependency Injection:** Database sessions, current user, and policy enforcers are injected cleanly into route handlers.

### 3. VMCF Control Plane
- **Intent Normalization:** Translates raw user requests into structured mission blueprints.
- **Policy Enforcement:** Applies pre-execution checks and risk validation.
- **Gateways:** All tool execution and LLM interactions are routed through deterministic `SafeToolGateway` and `ModelGateway` implementations.
- **Audit Logging:** Every mutating request is automatically intercepted by the `AuditMiddleware` and logged to the `AuditEvent` table.

### 4. Persistence Layer
- **Tech Stack:** SQLAlchemy ORM, Alembic migrations.
- **Supported Dialects:** PostgreSQL (Production) and SQLite (Development/Testing).
- **Core Models:** Users, Projects, Missions, Tasks, Events, Artifacts, Knowledge, Workflows, Audit Events.

## Architectural Invariants

1. **Frontend Isolation:** The frontend never orchestrates execution.
2. **Gateway Bottleneck:** Agents never call models or tools directly. Every call passes through the `ToolGateway` or `ModelGateway`.
3. **Implicit Deny:** Capability does not imply permission. 
4. **Untrusted Data:** Model and document content is treated as untrusted until validated.
5. **Strict Bounding:** Execution, retries, cost, and time are strictly bounded.
6. **Data Segregation:** Project-scoped data cannot cross project boundaries.
7. **Auditability:** Important decisions and state changes are immutable and auditable.
8. **Human Supremacy:** Human authority always supersedes agent authority.
