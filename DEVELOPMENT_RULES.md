# ============================================================

# VOID - DEVELOPMENT RULES

# ============================================================

## 1. PURPOSE

These rules define how VOID V1 is developed, tested, documented,
versioned, and handed off between coding agents.

The repository is the source of truth.

All implementation must remain consistent with:

- VOID_SPEC.md
- ARCHITECTURE.md
- SECURITY_RULES.md
- .clinerules
- BUILD_STATUS.md

---

## 2. DEVELOPMENT PRINCIPLE

VOID must be built as a real executable system.

Preferred engineering principle:

SIMPLE

- MODULAR
- TESTABLE
- SECURE
- OBSERVABLE
- EXTENSIBLE

Avoid unnecessary complexity.

Do not build infrastructure merely because the architecture diagram
contains a conceptual component.

A component should be implemented when it provides real V1 value.

---

## 3. IMPLEMENTATION ORDER

VOID must be implemented phase by phase.

The implementation order is defined by VOID_SPEC.md.

Do not skip foundational dependencies.

Do not implement future functionality merely because it is visible
in the final architecture.

Each phase must produce a usable and testable increment.

---

## 4. DEVELOPMENT CYCLE

Every phase follows:

IMPLEMENT
|
v
RUN
|
v
TEST
|
v
INSPECT
|
v
FIX
|
v
INTEGRATE
|
v
DOCUMENT
|
v
COMMIT
|
v
STOP

Never skip testing merely because the code appears correct.

---

## 5. GIT

Git is mandatory.

The repository uses:

main

The main branch should contain verified work.

Create commits at meaningful milestones.

Commit messages should be descriptive.

Recommended formats:

- feat: implement VMCF intent gate
- feat: add model gateway contracts
- fix: correct task state persistence
- test: add workflow execution tests
- docs: update architecture documentation
- security: restrict tool execution

---

## 6. WORKING TREE SAFETY

Before starting work:

    git status

Inspect existing changes.

Do not overwrite unrelated user changes.

Do not delete existing implementation merely because it was not
created by the current coding agent.

Preserve working functionality.

If unrelated uncommitted changes are discovered:

    STOP

unless the changes are clearly part of the current task.

---

## 7. AGENT HANDOFF

VOID may be developed by multiple coding agents.

For example:

GitHub Copilot
|
v
Git repository
|
v
Cline
|
v
Git repository

Every agent must inspect:

- BUILD_STATUS.md
- Git history
- existing implementation
- tests
- migrations
- configuration

Never assume what the previous agent completed.

The actual repository state is authoritative.

---

## 8. BUILD_STATUS.md

BUILD_STATUS.md must be updated after every completed phase.

It should contain:

- current phase
- completed phases
- current implementation status
- tests performed
- test results
- known limitations
- blockers
- important decisions
- latest commit
- next phase

Never mark unfinished functionality as completed.

---

## 9. ENVIRONMENT

VOID must prefer the existing development environment.

Current development baseline:

- Python 3.14.x
- Node.js 24.x
- PostgreSQL 18.x
- pgvector 0.8.x
- Ollama

Exact installed versions must be detected rather than blindly
replaced.

Use the project-local Python virtual environment:

    .venv

Do not install project dependencies globally.

---

## 10. DEPENDENCY MANAGEMENT

Python dependencies belong in:

    backend/requirements.txt

or an explicitly documented equivalent.

Frontend dependencies belong in the frontend package manager
configuration and lockfile.

Do not install random packages globally.

Before adding a dependency:

1. Determine whether the existing stack can solve the requirement.
2. Check whether the dependency is genuinely necessary.
3. Prefer mature and maintained packages.
4. Consider Python and Node compatibility.
5. Document important architectural dependencies.

Avoid dependency sprawl.

---

## 11. VERSION COMPATIBILITY

VOID should be version-aware.

Do not assume that a package version will remain permanently valid.

Technology-specific compatibility belongs behind:

- adapters
- compatibility definitions
- environment detection
- stable contracts

The VOID core should depend on abstractions.

Do not silently downgrade or upgrade installed software.

---

## 12. BACKEND ARCHITECTURE

Backend request flow should normally follow:

Controller
|
v
Service
|
v
Repository
|
v
Model

Business logic belongs primarily in services and domain components.

Controllers should remain thin.

Repositories should handle persistence concerns.

Models should represent domain and database state.

Do not place significant orchestration logic directly inside API routes.

---

## 13. FRONTEND ARCHITECTURE

The frontend is a presentation layer.

It communicates with backend APIs.

The frontend must not implement:

- mission orchestration
- model routing
- agent scheduling
- governance decisions
- tool authorization
- recovery decisions

Those responsibilities belong to the backend.

---

## 14. DATABASE

V1 uses:

PostgreSQL + pgvector

Database schema changes must use migrations.

Do not modify production schema manually as a replacement for
migrations.

Database access should be isolated behind the repository/data layer.

Do not silently replace PostgreSQL with SQLite.

---

## 15. CONFIGURATION

Configuration should be externalized.

Use environment variables and configuration files where appropriate.

Sensitive values must never be hardcoded.

Provide:

    .env.example

when environment configuration is required.

Never commit real secrets.

---

## 16. API DESIGN

API contracts must be explicit.

Use typed request and response models.

Validate incoming data.

Return structured errors.

Do not expose internal stack traces or secrets through API responses.

API behavior should be covered by tests.

---

## 17. CONTRACT-FIRST DEVELOPMENT

Important VOID components should communicate through explicit contracts.

Examples include:

- Mission
- ExecutionProfile
- DecisionRecord
- Task
- TaskState
- Agent
- Skill
- Tool
- Model
- Workflow
- Evidence
- Artifact
- Approval
- AuditEvent

Contracts should not depend unnecessarily on provider-specific
implementation details.

---

## 18. MODEL PROVIDERS

Provider-specific logic belongs inside model adapters.

Agents must use the Model Gateway.

Do not put provider SDK calls directly into agent implementations.

The core should remain provider-agnostic.

---

## 19. TOOLS

Tools must be registered and governed.

Tool execution must pass through the Tool Gateway.

Every tool should have appropriate:

- identity
- description
- input schema
- output schema
- permission requirements
- risk classification
- timeout
- budget
- audit behavior

Do not expose arbitrary tools to agents.

---

## 20. AGENTS

Agents are modular execution components.

An Agent Cell should define appropriate:

- identity
- role
- responsibilities
- non-responsibilities
- goal
- prompt
- prompt version
- context profile
- skills
- allowed tools
- model profile
- budget
- output schema
- validation requirements
- limitations
- tests

Do not create an agent when a simple function, skill, or direct
execution is sufficient.

Complexity must be earned by the task.

---

## 21. SKILLS

Skills are reusable capabilities.

A skill is not automatically an agent.

Skills should be:

- versioned
- registered
- tested
- permissioned
- traceable

Avoid duplicating the same capability across multiple agents.

---

## 22. WORK GRAPHS

Workflow execution should use explicit Work Graph structures.

A graph may contain:

- sequential tasks
- parallel tasks
- fan-out
- fan-in
- conditions
- validation
- revision
- human checkpoints

Avoid hidden orchestration logic scattered across agents.

---

## 23. TASK STATE

Task state must be persistent where required.

Important execution state must survive:

- retries
- application restarts
- failures
- approval pauses
- recovery
- cancellation

Do not rely on fragile in-memory state for critical execution state.

---

## 24. BOUNDED EXECUTION

All autonomous execution must have limits.

Use appropriate limits for:

- model calls
- tool calls
- retries
- graph iterations
- recovery attempts
- execution time
- token usage
- cost

No infinite loops.

---

## 25. VALIDATION

Important outputs must be validated.

Depending on the task, validation may include:

- schema validation
- quality validation
- evidence validation
- citation validation
- factuality checks
- policy validation
- artifact validation
- output contract validation
- safety validation

Do not assume model output is automatically correct.

---

## 26. RECOVERY

Recovery must be bounded and explicit.

Possible recovery actions include:

- retry
- revise
- replace model
- replace tool
- replan
- reduce scope
- request human input
- stop safely

Recovery must not create uncontrolled loops.

---

## 27. GOVERNANCE

Governance is independent from agent intent.

Policy decisions may result in:

- ALLOW
- ALLOW_WITH_LIMITS
- REVIEW
- APPROVAL_REQUIRED
- BLOCK
- ESCALATE

Agents cannot override governance decisions.

---

## 28. HUMAN APPROVAL

Human approval is required where defined by policy.

Examples include:

- high-impact actions
- irreversible actions
- sensitive operations
- restricted domains
- low-confidence decisions
- security-sensitive actions

Approval must be auditable.

---

## 29. AUDITABILITY

Important decisions must be reconstructable.

Record appropriate:

- actor
- mission
- task
- agent
- model
- tool
- policy decision
- approval
- validation
- recovery
- artifact
- timestamps
- errors

Do not sacrifice auditability for convenience.

---

## 30. LOGGING

Use structured logging.

Logs should help diagnose:

- startup failures
- API failures
- model failures
- tool failures
- workflow failures
- validation failures
- governance decisions
- recovery events

Never log secrets or unnecessary sensitive content.

---

## 31. TESTING PYRAMID

Use multiple testing levels.

Preferred order:

Unit
|
v
Component
|
v
Integration
|
v
API
|
v
Workflow
|
v
End-to-End

Security and regression tests must also be included where relevant.

---

## 32. TEST EVIDENCE

A test is PASS only when the expected behavior has actually been
executed and verified.

Do not mark tests as PASS because:

- code exists
- a function appears correct
- a route exists
- a class was created
- a mock returned the expected result

Use real execution wherever practical.

---

## 33. MOCKS

Mocks are allowed for isolated tests when appropriate.

Mocks must not be used to falsely claim that a real integration works.

Clearly distinguish:

- mocked test
- simulated environment
- real integration
- unavailable integration

---

## 34. DOCUMENTATION

Important architectural decisions must be documented.

Update documentation when implementation changes:

- architecture
- contracts
- security behavior
- workflows
- dependencies
- configuration
- compatibility behavior

---

## 35. CODE REVIEW MINDSET

Before considering a phase complete, inspect:

- correctness
- security
- maintainability
- test coverage
- error handling
- observability
- architectural compliance
- dependency impact

Ask:

    Does this implementation actually satisfy the VOID contract?

---

## 36. NO PREMATURE INFRASTRUCTURE

V1 should not introduce unnecessary:

- Docker
- Kubernetes
- Redis
- Kafka
- RabbitMQ
- Celery
- MongoDB
- Neo4j
- external vector databases
- broad connector ecosystems

unless the VOID specification explicitly requires them later.

Prefer the simplest infrastructure that satisfies V1.

---

## 37. NO SILENT FALLBACKS

Do not silently change:

- database
- model provider
- model
- runtime
- framework
- tool
- security policy

If a fallback is part of the design, it must be:

- explicit
- configured
- observable
- auditable

---

## 38. PERFORMANCE

Do not optimize prematurely.

First establish:

- correctness
- security
- testability
- observability

Then measure performance.

Optimize based on evidence.

---

## 39. FAILURE HANDLING

Failures must be explicit.

Use structured errors where practical.

A failure should communicate:

- what failed
- where it failed
- why it failed
- whether retry is possible
- whether human intervention is required
- what state was persisted

---

## 40. RELEASE READINESS

A phase is not complete merely because the code compiles.

Before completion verify:

- application startup
- database connectivity where applicable
- migrations
- API behavior
- relevant tests
- security controls
- logs
- documentation
- Git state
- BUILD_STATUS.md

---

## 41. FINAL RULE

The objective is not to produce the largest amount of code.

The objective is to produce a:

REAL
MODULAR
GOVERNED
TESTED
OBSERVABLE
SECURE
MAINTAINABLE

VOID V1.

Build only what the current phase requires.

Do not fake functionality.

Do not hide failures.

Do not silently change the architecture.

Do not proceed beyond the current phase without explicit instruction.

# ============================================================

# END OF VOID DEVELOPMENT RULES

# ============================================================
