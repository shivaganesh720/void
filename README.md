VOID
Versatile Orchestrated Intelligent Dispatcher
VOID is a governed AI operating system for work.
It converts human intent into controlled execution by selecting,
coordinating, validating, and supervising models, agents, skills,
tools, workflows, knowledge, memory, and artifacts.
VOID is designed around governance, bounded autonomy, persistence,
validation, security, observability, and provider independence.
Core Principle
User chooses WHAT.
User may choose HOW.
If the user does not choose HOW, VOID determines HOW.

What VOID Is
VOID is a control and execution plane for AI-powered work.
It provides structured mechanisms for:
intent understanding
mission control
capability selection
strategy resolution
work graph execution
agent orchestration
model abstraction
tool governance
validation
recovery
human approval
RAG and evidence
memory
artifacts
auditability
evaluation
compatibility management
What VOID Is Not
VOID is not:
User -> LLM -> Answer
VOID is not intended to be:
a simple chatbot
an LLM wrapper
a direct Agent -> Tool system
an uncontrolled agent swarm
a frontend orchestration engine
an agent-controlled governance system
Current Status
Version: V1.0
Current Phase: Phase 0 - Repository Foundation
Status: IN PROGRESS
Implementation: 0%
The development environment and repository foundation have been
established.
Application implementation has not yet started.
Architecture
High-level execution flow:
User
|
v
Presentation
|
v
Application API
|
v
VMCF
|
v
Execution Fabric
|
+----> Model Gateway
|
+----> Tool Gateway
|
+----> Agent Cells
|
v
Validation
|
v
Governance
|
v
Persistence
|
v
Artifacts / Results / Audit
VMCF
VOID Mission Control Fabric is the control plane.
Major components:
Intent Gate
Mission Kernel
Execution Control
Execution Profile
Capability Registry
Capability Broker
Strategy Resolver
Mission Blueprint
Pre-Execution Policy
Decision Controller
Execution Fabric
The execution layer contains:
Work Graph
Manager/Supervisor
Scheduler
Task State
Agent Cells
Agent Harness
Context Engine
Prompt Engine
Model Gateway
Tool Policy
Tool Gateway
Tool Cells
Result Merger
Governance
VOID uses explicit governance outcomes:
ALLOW
ALLOW_WITH_LIMITS
REVIEW
APPROVAL_REQUIRED
BLOCK
ESCALATE
Human authority remains above agent authority.
Agents cannot grant themselves permissions or bypass governance.
Security
VOID follows:
least privilege
deny by default
explicit authorization
capability != permission
external data != system instruction
bounded autonomy
tool allowlists
validation
auditability
safe failure
human approval for consequential actions
External documents, webpages, search results, RAG content, tool results,
and model outputs are treated as untrusted data unless explicitly
validated and authorized.
See:
SECURITY_RULES.md
Local-First V1
The initial V1 development environment is local-first.
Primary technology foundation:
Frontend
Next.js
React
TypeScript
HTML/CSS
optional React Flow
Backend
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
psycopg
Database
PostgreSQL
pgvector
Local Model Runtime
Ollama
The initial architecture does not require Docker, Kubernetes, Redis,
Kafka, RabbitMQ, Celery, MongoDB, Neo4j, or an external vector database.
Repository Structure
VOID/
|
+-- frontend/
|
+-- backend/
|
+-- docs/
|
+-- scripts/
|
+-- tests/
|
+-- .venv/
|
+-- .clinerules
+-- .gitignore
+-- VOID_SPEC.md
+-- ARCHITECTURE.md
+-- SECURITY_RULES.md
+-- DEVELOPMENT_RULES.md
+-- BUILD_STATUS.md
+-- README.md
Development Rules
VOID is developed incrementally.
Every phase follows:
IMPLEMENT
->
RUN
->
TEST
->
INSPECT
->
FIX
->
INTEGRATE
->
DOCUMENT
->
COMMIT
->
STOP
Do not implement future phases prematurely.
Do not fabricate functionality.
Do not silently change architecture.
Development Phases 0. Repository Foundation

1.  Contracts
2.  Project Foundation
3.  Compatibility Fabric
4.  VMCF
5.  Execution Fabric
6.  Model Gateway
7.  Tool Gateway
8.  Agents and Skills
9.  Validation and Recovery
10. Governance
11. RAG and Evidence
12. Memory and Artifacts
13. Workflows
14. Frontend
15. Compatibility Testing
16. Security and E2E
17. V1 Demonstration
    Initial V1 Agents
    The initial Agent Cells are:
    Research Agent
    Resume Intelligence Agent
    Learning Agent
    Validator Agent
    Optional agents such as Planner, Critic, and Document Agent will only
    be introduced when justified by actual requirements.
    Initial V1 Tools
    Candidate tools include:
    File Reader
    PDF Parser
    Web Search
    RAG Query
    Python Execution
    Artifact Generator
    Privileged tools remain governed and restricted.
    Proof Workflows
    V1 will demonstrate at least:
    Research
    Intent
    ->
    Strategy
    ->
    Research
    ->
    Evidence
    ->
    Validation
    ->
    Artifact
    ->
    Audit
    Resume and Job Description
    Resume
    ->
    Job Description
    ->
    Extraction
    ->
    Matching
    ->
    Validation
    ->
    Analysis
    ->
    Artifact
    Learning
    Learning Request
    ->
    Planning
    ->
    Content Generation
    ->
    Validation
    ->
    Learning Artifact
    Current Environment
    Current verified development environment:
    Windows
    Python 3.14.6
    Node.js 24.21.0
    npm 11.19.0
    Git 2.55.0.windows.3
    PostgreSQL 18.6
    pgvector 0.8.6
    Ollama 0.34.0
    PostgreSQL database:
    void_db
    PostgreSQL service:
    postgresql-x64-18
    Ollama API:
    http://localhost:11434
    At the current Phase 0 checkpoint, no Ollama model has been installed.
    Important V1 Invariants
    The following are mandatory:
    VMCF remains the control plane.
    Frontend does not orchestrate missions.
    Agents do not directly call model providers.
    Agents do not receive unrestricted tools.
    Tool access passes through the Tool Gateway.
    Governance remains independent from agents.
    Model output is untrusted until validated.
    External content is untrusted data.
    Execution is bounded.
    Recovery is bounded.
    Important state is persistent.
    Important decisions are auditable.
    PostgreSQL + pgvector is the V1 persistence foundation.
    Local-first execution is preferred.
    Provider implementations remain behind adapters.
    No silent architecture changes.
    No automatic production self-modification.
    Documentation
    Read these documents before modifying the project:
    Functional Specification
    VOID_SPEC.md
    Defines what VOID V1 is expected to do.
    Architecture
    ARCHITECTURE.md
    Defines how VOID is structured.
    Security
    SECURITY_RULES.md
    Defines security requirements and invariants.
    Development
    DEVELOPMENT_RULES.md
    Defines implementation, testing, Git, and development rules.
    Build Status
    BUILD_STATUS.md
    Defines the actual current implementation state and handoff information.
    Agent Rules
    .clinerules
    Defines the operating rules for AI coding agents working on the repository.
    Getting Started
    The project currently contains the repository foundation.
    Before application implementation:
    Activate the Python environment.
    .venv\Scripts\activate
    Verify the development environment.

Verify PostgreSQL is running.

Verify void_db exists.

Verify pgvector is installed.

Verify Ollama is running.

Review the project documentation.

Check Git status.

Complete Phase 0.

Begin Phase 1 - Contracts.

Important Development Rule
The repository is the source of truth.
Do not trust an agent's statement that a feature is complete.
Verify:
source code
executable behavior
tests
migrations
startup
logs
database state
security behavior
documentation
Git state
A feature is complete only when it is actually implemented, executable,
tested, verified, documented, and compliant with the VOID architecture
and security rules.
Project Philosophy
VOID is designed around a simple idea:
Human Intent
->
Governed Understanding
->
Controlled Dispatch
->
Bounded Execution
->
Validation
->
Governance
->
Persistence
->
Observable Result
The goal is not to build the largest AI system.
The goal is to build a real, governed, secure, modular, observable,
testable, and extensible AI operating system for work.
License
License information will be defined before public release.
Project Status
VOID V1 is currently under active development.
Current phase:
Phase 0 - Repository Foundation
Next checkpoint:
Phase 1 - Contracts
============================================================
