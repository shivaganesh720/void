# VOID Threat Model

**Status:** PARTIALLY_IMPLEMENTED

## Assets

User identity, project membership, uploaded resumes and job descriptions, mission state, execution decisions, evidence, artifacts, provider credentials, and audit records.

## Threat actors

Unauthenticated callers, an authenticated user attempting cross-project access, malicious uploaded documents, prompt-injection content, compromised model/tool providers, and accidental operator misconfiguration.

## Trust boundaries

The browser is untrusted. API requests cross an authentication and authorization boundary. Uploaded files, model output, tool output, and retrieved content are untrusted data and must not become policy or system instructions. Database access is server-side and must remain project-scoped.

## Attack paths and mitigations

| Attack path                         | Current mitigation                                                           | Status                |
| ----------------------------------- | ---------------------------------------------------------------------------- | --------------------- |
| Unsafe upload filename              | Basename and supported-extension validation                                  | IMPLEMENTED           |
| Oversized or empty upload           | Configured byte limit and size checks                                        | IMPLEMENTED           |
| Unsupported executable upload       | Extension and dangerous MIME rejection                                       | IMPLEMENTED           |
| Private data sent to external model | Pre-execution approval policy                                                | IMPLEMENTED           |
| Unsupported autonomous workflow     | Deterministic strategy resolver rejects unknown intent                       | IMPLEMENTED           |
| Invalid lifecycle mutation          | Central transition map rejects invalid transitions                           | IMPLEMENTED           |
| Cross-project data access           | Project-scoped database schema is prepared; request authorization is pending | PARTIALLY_IMPLEMENTED |
| Credential leakage                  | Environment configuration boundary; provider integration is disabled         | PARTIALLY_IMPLEMENTED |

## Residual risks

Authentication, request authorization, rate limiting, storage isolation, MIME signature inspection, malware scanning, audit integrity, CSRF strategy, and production secret management are not yet complete. PostgreSQL constraints and migration execution must be verified before claiming persistence readiness.

## Future work

Implement authenticated sessions, project-member dependency checks on every resource query, content-signature validation, isolated file storage, structured audit logging, security tests, and provider/tool gateways with deny-by-default permissions.
