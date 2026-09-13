# VOID Security Model

## Current controls

- Upload names reject path traversal and empty names.
- Upload size defaults to 10 MiB.
- Extensions are limited to PDF, DOCX, TXT, and Markdown.
- Executable MIME types, empty content, invalid UTF-8, malformed DOCX/PDF, and unreadable documents are rejected.
- Structured analysis is validated before result persistence in the development store.
- Logs use mission/task identifiers and generic workflow failure text; normal responses do not expose stack traces.
- CORS is configurable through `ALLOWED_ORIGINS`.

## Important boundary

There is no authentication middleware, session, user identity, or server-derived project membership. `project_id` is supplied by the client and only filters the in-memory store. A cross-project mismatch currently returns `404`, but this is not an authorization guarantee. Do not deploy this API with sensitive data.

## Missing controls

Durable access checks, tenant isolation, file signature and malware scanning, rate limiting, secret management, retention/deletion policy, audit persistence, CSRF/session policy, production headers, and database transaction tests are not implemented or verified. No API keys are required or logged because there is no provider integration.

## Release decision

The current controls support synthetic local demo data only. Public deployment requires identity, membership enforcement, persistent ownership checks for every mission/task/artifact/audit read, secure storage, operational limits, and an authorization test matrix.
