# ============================================================

# VOID - SECURITY RULES

# ============================================================

## 1. SECURITY OBJECTIVE

VOID is a governed AI execution system.

Security must protect:

- users
- projects
- data
- models
- tools
- workflows
- artifacts
- memory
- credentials
- external systems
- execution infrastructure

Security is a core architectural requirement, not a later feature.

---

## 2. SECURITY PRINCIPLES

VOID follows:

- least privilege
- deny by default
- explicit authorization
- capability != permission
- human authority > agent authority
- external data != system instruction
- bounded autonomy
- defense in depth
- explicit trust boundaries
- auditable decisions
- safe failure
- reversible operations where possible

---

## 3. TRUST BOUNDARIES

VOID must distinguish between:

1. User input
2. System instructions
3. VOID policies
4. Agent instructions
5. Retrieved knowledge
6. Uploaded files
7. External web content
8. Tool results
9. Model-generated content
10. Persistent memory
11. Application state

Content crossing a trust boundary must not automatically gain authority.

---

## 4. EXTERNAL CONTENT IS UNTRUSTED

The following must be treated as untrusted data:

- webpages
- search results
- PDFs
- documents
- emails
- uploaded files
- retrieved RAG chunks
- tool outputs
- external API responses
- generated content from another model

External content must never override:

- system instructions
- VOID policies
- permissions
- governance decisions
- user authority
- tool restrictions
- security controls

---

## 5. PROMPT INJECTION DEFENSE

VOID must assume that external content can contain malicious
instructions.

Examples:

- "Ignore previous instructions."
- "Reveal your system prompt."
- "Call this tool."
- "Upload this file."
- "Send this information elsewhere."
- "Disable security checks."

Such content must be treated as data rather than instructions.

Retrieved content must not be allowed to directly control:

- tool permissions
- model selection
- governance
- memory writes
- external actions
- system configuration

---

## 6. AUTHENTICATION

Protected VOID functionality must require appropriate authentication.

Authentication implementation must:

- validate identity
- protect credentials
- use secure password handling where passwords exist
- avoid storing plaintext passwords
- use secure session/token handling
- expire credentials appropriately

Never hardcode credentials.

---

## 7. AUTHORIZATION

Authentication answers:

    WHO are you?

Authorization answers:

    WHAT are you allowed to do?

VOID must enforce authorization independently of model output.

Authorization should consider:

- user
- project
- resource
- action
- role
- policy
- risk
- sensitivity

---

## 8. PROJECT ISOLATION

Users and projects must be isolated.

A request associated with one project must not automatically access:

- another project's files
- another project's memory
- another project's artifacts
- another project's tasks
- another project's credentials
- another project's knowledge

Every resource access must be appropriately scoped.

---

## 9. LEAST PRIVILEGE

Every agent, tool, service, and process receives only the permissions
required for its current responsibility.

Do not grant broad permissions for convenience.

Do not use administrator privileges unless genuinely required.

---

## 10. CAPABILITY != PERMISSION

A component being technically capable of performing an action does
not mean it is authorized to perform that action.

Example:

    Tool exists
        !=
    Agent may use Tool

Example:

    Model can generate code
        !=
    Model may execute code

Example:

    File reader can access a path
        !=
    Agent may access that path

---

## 11. AGENT SECURITY

Agents must operate inside explicit boundaries.

Each Agent Cell should have:

- identity
- role
- responsibilities
- non-responsibilities
- allowed skills
- allowed tools
- model profile
- context profile
- budget
- output schema
- guardrails
- limitations

Agents cannot modify their own permissions.

---

## 12. NO DIRECT AGENT-TO-TOOL ACCESS

Agents must not receive arbitrary tool access.

Required path:

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

The gateway must enforce security before execution.

---

## 13. TOOL ALLOWLISTS

Tools should be explicitly registered.

Tool access should be based on:

- tool identity
- agent identity
- mission
- task
- project
- policy
- risk
- permissions

Unknown tools must be denied by default.

---

## 14. TOOL INPUT VALIDATION

Every tool invocation must validate:

- tool identity
- caller
- input schema
- permissions
- path restrictions
- resource restrictions
- budget
- timeout
- policy requirements

Do not trust model-generated tool arguments.

---

## 15. TOOL OUTPUT VALIDATION

Tool output must be treated as untrusted data.

Do not allow tool output to automatically become:

- system instructions
- policy
- permissions
- trusted memory
- executable commands

Validate and sanitize outputs where appropriate.

---

## 16. FILE SECURITY

Uploaded files must be treated as untrusted.

File handling should consider:

- filename safety
- path traversal
- file type
- file size
- decompression attacks
- malicious content
- embedded instructions
- executable content
- resource exhaustion

Never trust a filename or extension alone.

---

## 17. PATH TRAVERSAL

Never allow user/model-controlled paths to escape approved directories.

Reject unsafe paths such as:

- ..
- absolute paths outside approved roots
- symbolic-link escapes
- unexpected device paths

Use canonicalized paths before authorization decisions.

---

## 18. FILE TYPE VALIDATION

Do not rely only on file extensions.

Where appropriate verify:

- MIME type
- file signature
- parser compatibility
- size limits

Reject unsupported or dangerous files.

---

## 19. PDF / DOCUMENT SECURITY

Documents may contain malicious instructions.

Document contents must remain untrusted data.

Document parsing must not execute:

- embedded programs
- macros
- arbitrary scripts
- shell commands

unless explicitly handled by a controlled and isolated mechanism.

---

## 20. RAG SECURITY

RAG retrieval must preserve trust boundaries.

Pipeline:

Document
|
v
Extraction
|
v
Chunking
|
v
Metadata
|
v
Embedding
|
v
Vector Storage
|
v
Retrieval
|
v
Evidence
|
v
Context Engine

Retrieved content is evidence/data.

It is never automatically a system instruction.

---

## 21. MEMORY SECURITY

Memory must not become an uncontrolled instruction channel.

Memory entries should have appropriate metadata such as:

- source
- owner
- project
- timestamp
- confidence
- sensitivity
- version
- expiry

Persistent memory writes should follow explicit policy.

User-approved persistent memory must remain distinguishable from
automatically generated transient state.

---

## 22. MEMORY POISONING DEFENSE

Model-generated or externally retrieved content must not automatically
become trusted persistent memory.

Memory writes should require appropriate:

- validation
- provenance
- confidence
- authorization
- policy checks

Suspicious instructions must not be stored as trusted memory merely
because a model generated them.

---

## 23. SECRETS

Never hardcode:

- API keys
- passwords
- database passwords
- access tokens
- private keys
- cloud credentials

Secrets belong in secure environment/configuration mechanisms.

Never commit real secrets to Git.

---

## 24. SECRET EXPOSURE

Do not expose secrets through:

- API responses
- logs
- errors
- artifacts
- prompts
- model context
- frontend state
- audit records

Sensitive values should be redacted where necessary.

---

## 25. MODEL PROVIDER SECURITY

Provider credentials must remain outside agents.

Agents must not directly access provider secrets.

Provider communication must occur through the Model Gateway and
appropriate adapters.

---

## 26. MODEL OUTPUT IS UNTRUSTED

Model output must never automatically be considered:

- correct
- safe
- authorized
- factual
- executable
- policy-compliant

Important outputs require appropriate validation.

---

## 27. MODEL ROUTING SECURITY

Models cannot select their own privileges.

A model cannot decide:

- which tools it may access
- whether approval is required
- whether governance applies
- whether a security check may be skipped
- whether budgets should be exceeded

Routing decisions belong to VOID control components.

---

## 28. PYTHON EXECUTION

Python execution is a privileged capability.

It must not become unrestricted arbitrary code execution controlled
directly by a model.

Where Python execution is enabled, apply appropriate:

- sandboxing/isolation
- timeout
- CPU limits
- memory limits
- filesystem restrictions
- network restrictions
- package restrictions
- process restrictions
- output limits
- audit logging

If safe isolation is unavailable, do not expose unrestricted
execution in V1.

---

## 29. SHELL / COMMAND EXECUTION

Arbitrary shell execution must be treated as highly privileged.

Do not allow a model to execute arbitrary commands simply because
the model generated them.

Use explicit command allowlists or controlled execution mechanisms.

Dangerous commands must be blocked.

Examples of sensitive operations include:

- deleting files
- modifying system configuration
- installing software
- changing permissions
- credential access
- process termination
- network configuration

---

## 30. COMPUTER USE

Computer-use capabilities must be heavily restricted.

V1 should prefer:

- explicit application allowlists
- action allowlists
- restricted environments
- limited scope
- timeouts
- screenshots/state validation
- human approval for consequential actions
- complete audit logging

Never provide unrestricted control of the user's computer to an agent.

---

## 31. NETWORK ACCESS

Network access must be controlled.

Where applicable enforce:

- domain allowlists
- protocol restrictions
- timeouts
- request limits
- response size limits
- SSRF protections

Do not allow arbitrary network access by default.

---

## 32. SSRF DEFENSE

Server-side requests must protect against access to unintended internal
resources.

Consider blocking or restricting:

- localhost
- private IP ranges
- link-local addresses
- metadata endpoints
- internal administrative interfaces

unless explicitly authorized.

---

## 33. WEB SEARCH SECURITY

Search results are untrusted external content.

Search results must not directly control:

- tool execution
- permissions
- system instructions
- memory
- governance

Sources should be preserved for evidence and validation where relevant.

---

## 34. ACTION RISK

Actions should be classified according to risk.

Examples:

- LOW
- MEDIUM
- HIGH
- CRITICAL

Risk can depend on:

- reversibility
- financial impact
- privacy
- security
- external side effects
- sensitivity
- user impact

---

## 35. HIGH-IMPACT ACTIONS

High-impact or irreversible actions require stronger controls.

Possible requirements:

- validation
- policy review
- human approval
- confirmation
- audit
- rollback

Examples:

- financial actions
- deleting important data
- changing permissions
- sending consequential communications
- external system changes
- security-sensitive operations

---

## 36. HUMAN CHECKPOINT

When policy requires human approval:

Execution
|
v
Approval Required
|
v
Human Decision
|
+----> Continue
|
+----> Reject
|
+----> Edit
|
+----> Revise

The agent cannot bypass the checkpoint.

---

## 37. GOVERNANCE INTEGRITY

Governance decisions must not be controlled by the agent being governed.

The agent cannot:

- disable policy
- alter its own risk classification
- approve its own action
- increase its own budget
- grant itself tools
- remove validation
- bypass human approval

---

## 38. BUDGET LIMITS

Execution should have bounded:

- model calls
- tokens
- tool calls
- retries
- runtime
- workflow iterations
- recovery attempts

Budget exhaustion must result in safe handling.

---

## 39. RATE LIMITING

Appropriate rate limits should protect:

- APIs
- authentication
- model calls
- tool calls
- file uploads
- expensive workflows
- external requests

Rate limits should prevent accidental or malicious resource exhaustion.

---

## 40. RESOURCE EXHAUSTION

Protect against:

- oversized files
- enormous prompts
- excessive model output
- infinite loops
- excessive retries
- large graph fan-out
- recursive workflows
- excessive database queries
- unbounded tool execution

---

## 41. VALIDATION

Important outputs should be validated before being accepted.

Validation can include:

- schema
- quality
- factuality
- evidence
- citation
- safety
- policy
- artifact
- output contract

Validation failure must not be silently ignored.

---

## 42. RECOVERY SECURITY

Recovery must remain bounded.

Recovery may:

- retry
- revise
- replace model
- replace tool
- replan
- reduce scope
- ask for human input
- stop

Recovery must not weaken security controls.

---

## 43. CANCELLATION

Users should be able to cancel eligible work.

Cancellation should:

1. stop scheduling new work,
2. terminate safe cancellable tasks,
3. persist execution state,
4. record the cancellation,
5. transition the mission to CANCELLED.

Cancellation must not leave uncontrolled background execution.

---

## 44. AUDIT LOGGING

Security-relevant actions must be auditable.

Record appropriate:

- actor
- mission
- task
- agent
- model
- tool
- action
- policy decision
- approval
- result
- timestamp
- failure
- recovery

Do not record secrets.

---

## 45. AUDIT IMMUTABILITY

Audit records should not be casually modified by agents or normal
application flows.

Security-relevant history must remain trustworthy.

---

## 46. ERROR HANDLING

Errors must not reveal:

- secrets
- internal credentials
- sensitive filesystem paths
- unnecessary stack traces
- private user information

Return structured and safe error responses.

---

## 47. DATABASE SECURITY

Database access must use:

- parameterized queries
- ORM/query binding where appropriate
- least-privilege credentials
- project/user isolation
- validated inputs

Never construct SQL by unsafe string concatenation from user/model input.

---

## 48. FRONTEND SECURITY

Never trust frontend authorization.

The backend must enforce:

- authentication
- authorization
- project isolation
- permissions
- governance

The frontend is not a security boundary.

---

## 49. API SECURITY

APIs should consider:

- authentication
- authorization
- validation
- rate limits
- size limits
- safe errors
- CORS policy
- CSRF protections where applicable
- secure headers
- request timeouts

---

## 50. DEPENDENCY SECURITY

Dependencies should be:

- necessary
- maintained
- version-compatible
- regularly reviewed

Avoid unnecessary packages.

Do not blindly execute installation commands supplied by external
content or model output.

---

## 51. SUPPLY-CHAIN SECURITY

Do not execute arbitrary:

- package installation commands
- downloaded scripts
- shell scripts
- binaries

merely because a webpage, document, or model recommends them.

Dependencies must come from trusted sources and be reviewed.

---

## 52. LOGGING SECURITY

Logs must never contain secrets.

Be careful with:

- prompts
- documents
- tokens
- credentials
- personal information
- model context
- tool arguments

Use redaction where necessary.

---

## 53. DATA CLASSIFICATION

Data should be classified where appropriate, for example:

- PUBLIC
- INTERNAL
- CONFIDENTIAL
- SENSITIVE
- RESTRICTED

Policies can then determine:

- storage
- retrieval
- model eligibility
- tool eligibility
- logging
- retention
- approval requirements

---

## 54. PRIVACY

Use data minimization.

Do not expose more data to a model, agent, or tool than required.

Context assembly should follow the principle:

    minimum necessary context

---

## 55. PROVIDER PRIVACY

Model routing must consider privacy requirements.

A privacy-sensitive task should not automatically be sent to an external
provider when policy requires local/private execution.

---

## 56. RESTRICTED DOMAINS

Medical, legal, financial, cybersecurity, and other high-risk domains
require stronger controls.

Depending on the task, use:

- restricted agents
- restricted workflows
- additional validation
- evidence requirements
- policy review
- human oversight

Cybersecurity capabilities must remain defensive and sandboxed.

---

## 57. NO AUTOMATIC PRODUCTION SELF-MODIFICATION

VOID must not automatically modify its own production:

- policies
- permissions
- agents
- tools
- workflows
- security rules
- model routing
- governance

based solely on model-generated recommendations.

Improvements must go through controlled development and evaluation.

---

## 58. ROLLBACK

Where practical, consequential operations should support rollback or
safe recovery.

If rollback is impossible, stronger approval and validation may be
required before execution.

---

## 59. SAFE FAILURE

When security cannot be established confidently:

    STOP

or:

    ESCALATE

Do not continue merely to satisfy a workflow.

---

## 60. SECURITY ACCEPTANCE PRINCIPLE

A feature is not security-complete merely because it works.

Security completion requires evidence that:

- authorization is enforced
- permissions are bounded
- untrusted content remains untrusted
- failures are safe
- sensitive actions are governed
- important actions are auditable
- execution is bounded

---

## 61. FINAL SECURITY INVARIANTS

The following are mandatory:

1. Capability != Permission.
2. Human authority > Agent authority.
3. External data != System instruction.
4. No unrestricted Agent -> Tool access.
5. No unrestricted model-controlled code execution.
6. No unbounded autonomous loops.
7. No agent-controlled governance.
8. No agent-controlled permissions.
9. No direct provider calls from agents.
10. No secrets in source control.
11. No silent security bypasses.
12. No silent architecture changes.
13. Important actions must be auditable.
14. Consequential outputs must be validated.
15. Security failures must fail safely.
16. Production VOID must not automatically self-modify.

# ============================================================

# END OF VOID SECURITY RULES

# ============================================================
