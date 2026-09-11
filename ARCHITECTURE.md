# VOID - ARCHITECTURE

## 1. PURPOSE

VOID (Versatile Orchestrated Intelligent Dispatcher) is a governed AI
operating system for work.

VOID converts human intent into controlled execution by selecting,
coordinating, validating, and supervising:

- models
- agents
- skills
- tools
- workflows
- knowledge
- memory
- artifacts

according to:

- user preferences
- system policies
- permissions
- risk
- privacy
- quality
- cost
- latency
- execution constraints

The architecture is designed to be:

- modular
- provider-agnostic
- version-aware
- secure
- observable
- testable
- extensible
- governed

---

## 2. CORE PRINCIPLE

> User chooses WHAT.
>
> User may choose HOW.
>
> If the user does not choose HOW, VOID determines HOW.

VOID therefore separates:

1. human intent
2. control and decision making
3. execution
4. governance
5. validation
6. persistence
7. evaluation

---

## 3. WHAT VOID IS NOT

VOID is not:

```text
User -> LLM -> Answer
VOID is not:
a chatbot wrapper
a single LLM application
a direct Agent -> Tool architecture
an uncontrolled agent swarm
a frontend-driven orchestration system
a collection of independent agents without governance
a system where models control their own permissions
a system where agents directly call model providers
a system where external content becomes trusted instructions
VOID is a governed control and execution plane.
4. SYSTEM BOUNDARY
At a high level:
+---------------------------------------------------------------+
|                            USER                               |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                    PRESENTATION LAYER                         |
|  Command | Mission Dashboard | Details | Graph | Artifacts    |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                     APPLICATION API                           |
| Auth | Projects | Sessions | Mission API | Artifact API       |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                VOID MISSION CONTROL FABRIC                    |
|                                                               |
| Intent Gate -> Mission Kernel -> Strategy -> Policy           |
| Capability Registry/Broker -> Blueprint -> Decision Control  |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                     EXECUTION FABRIC                           |
| Work Graph -> Manager -> Scheduler -> Task State              |
| Agent Cells -> Harness -> Context -> Prompt -> Model Gateway  |
| Tool Policy -> Tool Gateway -> Tool Cells -> Result Merger    |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                  VALIDATION / GOVERNANCE                       |
| Validation | Policy | Approval | Recovery | Audit              |
+-------------------------------+-------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|                       PERSISTENCE                              |
| PostgreSQL | pgvector | Evidence | Memory | Artifacts | Audit |
+---------------------------------------------------------------+
5. ARCHITECTURAL PLANES
VOID is organized into major logical planes.
Presentation Plane
Responsible for:
user interaction
mission visibility
execution visibility
approvals
artifacts
configuration
It does not orchestrate missions.
Application Plane
Responsible for:
authentication
project/session management
API contracts
application services
resource access
Control Plane
Implemented primarily by VMCF.
Responsible for:
understanding intent
mission creation
capability resolution
strategy selection
policy decisions
execution planning
execution control
Execution Plane
Implemented by the Execution Fabric.
Responsible for:
task scheduling
agent execution
model calls
tool calls
state transitions
result merging
Governance Plane
Responsible for:
authorization
risk
policy
budgets
approval
validation
escalation
recovery constraints
Persistence Plane
Responsible for:
missions
tasks
state
decisions
evidence
artifacts
memory
audit
evaluations
Compatibility Plane
Responsible for:
runtime detection
provider compatibility
capability compatibility
version resolution
adapter selection
6. REQUEST TO RESULT FLOW
A typical request follows:
User Intent
    |
    v
Intent Gate
    |
    v
Mission Kernel
    |
    v
Execution Profile
    |
    v
Capability Resolution
    |
    v
Strategy Resolver
    |
    v
Pre-Execution Policy
    |
    v
Mission Blueprint
    |
    v
Decision Controller
    |
    v
Work Graph
    |
    v
Scheduler
    |
    v
Agent Cell / Tool / Model
    |
    v
Task Result
    |
    v
Validation
    |
    +----> Recovery
    |
    +----> Human Approval
    |
    v
Result Merger
    |
    v
Artifact / Result
    |
    v
Persistence + Audit
7. VMCF
7.1 Overview
VMCF means:
VOID Mission Control Fabric
VMCF is the control plane responsible for turning user intent into a
governed executable mission.
VMCF should not directly perform every task.
It decides and controls how work is executed.
7.2 Intent Gate
Responsibilities:
receive user intent
normalize input
identify task type
identify constraints
identify explicit user preferences
identify missing information
identify risk signals
create a mission request
The Intent Gate must not blindly trust model-generated interpretation.
7.3 Mission Kernel
The Mission Kernel creates and manages the logical mission.
Responsibilities:
mission identity
mission lifecycle
mission metadata
user/project association
execution state
mission cancellation
mission pause/resume
mission completion
7.4 Execution Control
Execution Control manages:
start
pause
resume
cancel
retry
recover
approval
escalation
It controls execution without becoming a hidden task implementation layer.
7.5 Execution Profile
An ExecutionProfile describes how a mission should be executed.
It may contain:
mode
strategy
model
fallback_model
agents
skills
tools
workflow
context_profile
rag_policy
memory_policy
validation_policy
budget
latency_target
quality_target
privacy_requirement
approval_policy
user_constraints
Each important decision should retain:
value
source
reason
confidence
timestamp
Possible decision sources:
USER
AUTO_ROUTER
POLICY
SYSTEM_DEFAULT
7.6 Capability Registry
The Capability Registry describes available capabilities.
Examples:
models
agents
skills
tools
workflows
runtimes
providers
The registry describes capability.
It does not automatically grant permission.
7.7 Capability Broker
The Capability Broker resolves usable capabilities based on:
task requirements
project
permissions
policy
privacy
availability
compatibility
risk
budget
7.8 Strategy Resolver
The Strategy Resolver determines how the mission should be executed.
V1 should prefer deterministic and explainable routing.
The Strategy Resolver should consider:
task type
user mode
required capabilities
quality target
latency target
privacy
cost
risk
available models
available agents
available tools
workflow requirements
V1 should not depend on an uncontrolled "model council".
7.9 Mission Blueprint
The Mission Blueprint is the executable mission plan.
It may contain:
mission metadata
execution profile
work graph
tasks
dependencies
agents
skills
tools
models
validation requirements
approval checkpoints
recovery policies
budgets
7.10 Pre-Execution Policy
Before execution begins, policy should evaluate:
authorization
risk
tools
model/provider
privacy
budget
domain restrictions
approval requirements
Possible outcomes:
ALLOW
ALLOW_WITH_LIMITS
REVIEW
APPROVAL_REQUIRED
BLOCK
ESCALATE
7.11 Decision Controller
The Decision Controller coordinates control decisions while preserving
separation between:
user authority
system policy
agent suggestions
execution state
Agents can propose actions.
Control components determine whether those actions are allowed.
8. EXECUTION FABRIC
8.1 Work Graph
The Work Graph is the explicit representation of executable work.
It supports:
task nodes
dependencies
sequential execution
parallel execution
fan-out
fan-in
conditions
validation
revision
approval checkpoints
recovery paths
8.2 Manager / Supervisor
The Manager coordinates execution.
Responsibilities:
monitor tasks
maintain execution state
coordinate graph progress
request validation
trigger bounded recovery
report failures
escalate when required
The Manager is not a free-form autonomous controller.
Its authority is constrained by:
mission policy
execution profile
budgets
tool permissions
graph structure
governance
8.3 Scheduler
The Scheduler determines when eligible tasks can execute.
It considers:
dependencies
task state
resource limits
concurrency limits
budgets
policy
cancellation
approvals
8.4 Task State
TaskState is persistent execution state.
It should represent:
task identity
mission identity
status
inputs
outputs
dependencies
attempts
errors
timestamps
validation state
recovery state
approval state
8.5 Agent Cells
An Agent Cell is a bounded execution unit.
An Agent Cell contains:
identity
role
responsibilities
non-responsibilities
prompt
prompt version
context profile
model profile
skills
allowed tools
budget
output schema
limitations
tests
An Agent Cell does not own global governance.
8.6 Agent Harness
The Harness controls the execution environment around an Agent Cell.
It may handle:
context assembly
prompt construction
model invocation
output parsing
tool requests
iteration limits
timeout
budget
logging
validation hooks
The Harness must remain bounded.
8.7 Context Engine
The Context Engine constructs the minimum necessary context.
Possible context sources:
user input
mission state
task state
approved memory
RAG evidence
tool results
previous task outputs
system policy
agent instructions
External content remains untrusted.
8.8 Prompt Engine
The Prompt Engine manages:
system instructions
agent instructions
task instructions
context assembly
output schema
prompt version
prompt metadata
Prompts should be versioned where important.
9. MODEL GATEWAY
The Model Gateway is the only normal model-provider entry point for
agents and execution components.
Architecture:
Agent / Harness
       |
       v
Model Gateway
       |
       +----> Ollama Adapter
       |
       +----> OpenAI Adapter
       |
       +----> Anthropic Adapter
       |
       +----> Google Adapter
       |
       +----> Other Provider Adapters
V1 begins local-first with Ollama.
Provider adapters should isolate provider-specific APIs.
9.1 Model Capability Classes
V1 may define capability classes such as:
ROUTER_FAST
GENERAL_WORKER
REASONING_PREMIUM
RESEARCH_EVIDENCE
VISION_DOCUMENT
CODING
LOCAL_PRIVATE
DOCUMENT_PARSE
TRANSLATION
CREATIVE_MEDIA
RESTRICTED_DOMAIN
COMPUTER_USE
A capability class is not itself a permission.
9.2 Model Modes
User-facing model modes may include:
AUTO
HIGH QUALITY
LOW COST
FAST
PRIVATE
MANUAL
Governance still applies in every mode.
10. TOOL FABRIC
Required architecture:
Agent
  |
  v
Tool Policy
  |
  v
Tool Gateway
  |
  v
Tool Cell
  |
  v
Execution
The Tool Gateway is responsible for:
identity
authorization
input validation
risk checks
budget checks
execution
output validation
audit
Candidate V1 tools include:
File Reader
PDF Parser
Web Search
RAG Query
Python Execution
Artifact Generator
Privileged tools require stronger restrictions.
11. GOVERNANCE
Governance is a cross-cutting control system.
Governance evaluates:
identity
authorization
risk
privacy
sensitivity
tool use
model/provider
budget
external side effects
approval requirements
Possible outcomes:
ALLOW
ALLOW_WITH_LIMITS
REVIEW
APPROVAL_REQUIRED
BLOCK
ESCALATE
Governance must remain independent of the agent being governed.
12. VALIDATION
Validation occurs after important execution steps.
Validation may include:
schema validation
output contract validation
factuality
evidence
citations
policy
safety
artifact correctness
quality
Validation failures may trigger:
revision
retry
recovery
human review
safe stop
13. RECOVERY
Recovery is explicit and bounded.
Possible recovery actions:
retry
revise
replace model
replace tool
replan
reduce scope
request human intervention
stop
Recovery must preserve:
security
governance
budgets
auditability
14. PERSISTENCE
V1 persistence uses:
PostgreSQL + pgvector
Persistence should include:
users
projects
sessions
missions
tasks
task state
decisions
policies
approvals
evidence
artifacts
memory
audit events
evaluations
Database schema changes must use migrations.
15. RAG AND EVIDENCE
RAG is an evidence system, not an instruction system.
Pipeline:
Document
    |
    v
Parse
    |
    v
Normalize
    |
    v
Chunk
    |
    v
Metadata
    |
    v
Embedding
    |
    v
pgvector
    |
    v
Retrieve
    |
    v
Evidence
    |
    v
Context Engine
Evidence should preserve appropriate provenance such as:
source
document
location
timestamp
relevance
retrieval information
Retrieved content remains untrusted data.
16. MEMORY
VOID distinguishes:
Transient Context
Short-lived information needed for a task.
Workflow State
Execution state required to continue a mission.
Persistent Memory
Information intentionally retained across missions.
Knowledge
Retrieved or stored reference information.
These concepts must not be conflated.
Memory writes require appropriate policy and provenance.
17. ARTIFACTS
Artifacts are durable outputs produced by missions.
Examples:
reports
documents
analyses
tables
datasets
code artifacts
learning materials
Artifacts should have:
identity
type
source mission
source task
version
creation time
validation state
provenance
18. AUDIT AND OBSERVABILITY
Important events should be observable.
Audit information may include:
mission
task
user
agent
model
tool
policy
approval
validation
recovery
artifact
error
timestamp
Observability should provide enough information to reconstruct
important execution decisions.
Secrets must not be logged.
19. COMPATIBILITY FABRIC
VOID must remain resilient to changing versions and providers.
The Compatibility Fabric may contain:
Runtime Registry
Environment Detector
Version Resolver
Dependency Resolver
Capability Resolver
Adapter Registry
Compatibility Matrix
The purpose is to separate stable VOID contracts from changing
technology implementations.
20. BACKEND LAYERING
Recommended backend structure:
API / Controller
       |
       v
Application Service
       |
       v
Domain / Control / Execution Logic
       |
       v
Repository
       |
       v
Database Model
The VMCF and Execution Fabric remain domain/control components.
Do not place orchestration logic directly in HTTP routes.
21. FRONTEND
The frontend should provide:
Universal Command
Mission Dashboard
Execution Control
Mission Details
Work Graph
Run Details
Approval Interface
Artifacts
Memory
Workflow Views
Evaluation
Settings
The frontend is presentation only.
It communicates with backend APIs.
22. API AND CONTRACTS
Important APIs should use explicit contracts.
Examples:
mission creation
mission status
mission cancellation
task status
approval
artifact retrieval
memory operations
workflow operations
evaluation results
Contracts should be versionable.
23. VERSION INDEPENDENCE
VOID must remain independent of individual provider implementations.
For example:
VOID Contract
    |
    v
Adapter Interface
    |
    +----> Provider A
    +----> Provider B
    +----> Provider C
    +----> Local Provider
Changing a provider should not require redesigning the control plane.
24. LOCAL-FIRST V1 DEPLOYMENT
The initial V1 development target is local-first.
Primary components:
Next.js frontend
FastAPI backend
PostgreSQL
pgvector
Ollama
V1 does not require:
Docker
Kubernetes
Redis
Kafka
RabbitMQ
Celery
MongoDB
Neo4j
external vector database
unless a later phase explicitly requires one.
25. INITIAL V1 AGENTS
Initial Agent Cells:
Research Agent
Resume Intelligence Agent
Learning Agent
Validator Agent
Optional:
Planner Agent
Critic Agent
Document Agent
Optional agents should only be added when they provide demonstrated
value.
26. INITIAL V1 WORKFLOWS
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
27. V1 NON-GOALS
The following are not required for the initial V1 unless explicitly
added through a later approved phase:
unrestricted computer control
unrestricted shell execution
unrestricted code execution
autonomous production self-modification
uncontrolled agent swarms
large microservice architecture
Kubernetes deployment
broad enterprise connector ecosystem
uncontrolled multi-provider complexity
model councils as the default routing mechanism
28. ARCHITECTURAL INVARIANTS
The following cannot be bypassed without explicit architecture review:
VMCF remains the control plane.
Execution remains governed.
Frontend remains presentation-focused.
Agents do not directly call model providers.
Agents do not receive unrestricted tools.
Tool execution passes through the Tool Gateway.
Governance remains independent from agents.
Validation remains part of important execution.
Recovery remains bounded.
Important state remains persistent.
Important decisions remain auditable.
External content remains untrusted.
PostgreSQL + pgvector remains the V1 persistence/vector foundation.
Local-first execution remains preferred.
Provider implementations remain behind adapters.
V1 avoids unnecessary infrastructure.
No automatic production self-modification.
29. ARCHITECTURE CHANGE CONTROL
A major architectural change requires:
Stop implementation.
Identify the conflict or limitation.
Explain the proposed change.
Explain affected components.
Explain security impact.
Explain migration impact.
Explain compatibility impact.
Obtain explicit approval.
Update architecture documentation.
Update BUILD_STATUS.md.
Implement only after approval.
Coding agents must not silently redesign VOID.
30. PHASE MAPPING
Architecture implementation follows:
Phase 0  -> Repository Foundation
Phase 1  -> Contracts
Phase 2  -> Project Foundation
Phase 3  -> Compatibility Fabric
Phase 4  -> VMCF
Phase 5  -> Execution Fabric
Phase 6  -> Model Gateway
Phase 7  -> Tool Gateway
Phase 8  -> Agents and Skills
Phase 9  -> Validation and Recovery
Phase 10 -> Governance
Phase 11 -> RAG and Evidence
Phase 12 -> Memory and Artifacts
Phase 13 -> Workflows
Phase 14 -> Frontend
Phase 15 -> Compatibility Testing
Phase 16 -> Security and E2E
Phase 17 -> V1 Demonstration
31. FINAL ARCHITECTURAL PRINCIPLE
VOID should remain:
governed
modular
provider-agnostic
capability-aware
permission-aware
persistent
observable
testable
secure
bounded
extensible
The architecture exists to support real execution.
Do not implement architecture as decoration.
Do not simplify away governance.
Do not replace the control plane with direct model calls.
Do not replace Work Graph execution with uncontrolled sequential code.
Build the smallest genuinely functional implementation that satisfies
the architectural contract.
============================================================
END OF ARCHITECTURE.md
============================================================
```
