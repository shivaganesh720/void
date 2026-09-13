# VOID Threat Model

**Status:** PARTIALLY_IMPLEMENTED
**Reviewed:** 2026-09-13

## Assets

User identities, project membership, uploaded resumes and job descriptions, mission state, execution decisions, evidence, artifacts, provider credentials, and audit records.

## Threat actors

Unauthenticated callers, users attempting cross-project access, malicious documents, prompt-injection content, compromised providers, malicious tools, and operator misconfiguration.

## Trust boundaries

The browser, API caller, uploaded file, model, tool, retrieved content, and persistent memory are untrusted boundaries. Only validated server-side policy and authorization decisions may grant access or permission.

## Main threats and mitigations

| Threat                          | Current mitigation                                 | Status          |
| ------------------------------- | -------------------------------------------------- | --------------- |
| Unsafe filename or traversal    | Basic basename validation                          | PARTIAL         |
| Oversized or empty upload       | Size and emptiness checks                          | IMPLEMENTED     |
| Unsupported executable upload   | Extension and dangerous MIME checks                | PARTIAL         |
| Private data sent externally    | Approval policy primitive                          | IMPLEMENTED     |
| Unsupported autonomous workflow | Deterministic strategy rejection                   | IMPLEMENTED     |
| Invalid state mutation          | Central transition validation                      | IMPLEMENTED     |
| Cross-project access            | Scoped model design; request authorization pending | NOT_IMPLEMENTED |
| Secret leakage                  | Environment template; providers disabled           | PARTIAL         |

## Residual risks

Authentication, authorization, storage isolation, MIME signature inspection, malware scanning, rate limiting, CSRF review, audit integrity, and security integration tests are missing.

## Required next controls

1. Authenticate every protected request.
2. Check project membership on every project-scoped query.
3. Store files outside public paths with generated identifiers.
4. Validate file signatures and parser behavior.
5. Redact sensitive logs and error responses.
6. Add cross-project, replay, path-traversal, MIME, policy-bypass, and secret-leakage tests.
