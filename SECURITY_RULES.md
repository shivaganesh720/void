# VOID Security Rules

## Core principles

- Deny by default.
- Least privilege.
- Capability is separate from permission.
- Human authority is above agent authority.
- External content is data, not instructions.
- Governance cannot be overridden by a model or agent.
- Sensitive actions require review or approval.
- Important decisions are auditable.

## Trust boundaries

Treat browser input, uploaded documents, model output, tool output, retrieved content, and persistent memory as untrusted. They must not change policies, permissions, system instructions, or tool allowlists.

## Required controls

### Identity and authorization

Require authentication for protected operations. Authorize every resource by user, project, role, action, risk, and sensitivity. Never trust client-provided permissions.

### Project isolation

Every project-scoped resource must be filtered by project membership. Cross-project access must fail closed and be covered by security tests.

### Files

Reject unsafe paths, traversal, empty files, oversized files, unsupported extensions, dangerous MIME types, corrupt files, and MIME/signature mismatches. Do not execute document macros or embedded programs. Scanned PDFs are unsupported until OCR is implemented safely.

### Models and tools

Models are accessed only through the Model Gateway. Tools are accessed only through the Tool Gateway. Shell execution, arbitrary code execution, browser control, unrestricted network access, and external side effects are disabled by default.

### Logging and secrets

Never log passwords, API keys, tokens, full sensitive documents, or unnecessary personal data. Return user-safe errors and keep stack traces in secure server logs only.

## Current status

Implemented and tested: basic upload checks, private external-model approval logic, and rejection of unknown workflows.

Pending: authentication, project authorization, storage isolation, file signature inspection, malware scanning, rate limiting, CSRF review, audit integrity, and security integration tests.
