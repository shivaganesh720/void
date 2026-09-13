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

The local API includes bearer-token registration/login, current-user, logout, and server-side project membership checks. Mission requests must carry the access token. User/project identity is still held in the local runtime rather than a durable identity/session repository, so this is not production deployment security.

## Missing controls

Refresh-token rotation, durable sessions, rate limiting, file signature and malware scanning, retention/deletion policy, audit persistence, CSRF/session policy, production headers, and database transaction integration are not implemented or verified. No API keys are required or logged because there is no provider integration.

## Release decision

The current controls support synthetic local demo data only. Public deployment requires identity, membership enforcement, persistent ownership checks for every mission/task/artifact/audit read, secure storage, operational limits, and an authorization test matrix.
