# VOID Database Status

SQLAlchemy/PostgreSQL entity definitions exist in `backend/app/db/base.py` for users, projects, members, missions, tasks, artifacts, and audit events. The current local runtime additionally uses `backend/app/db/runtime.py`, a small SQLite payload store at `.local/void.sqlite3`, with an idempotent schema migration artifact at `scripts/migrations/001_runtime_store.sql`.

The API hydrates missions from SQLite at startup and persists mission, task, result, timestamp, and lifecycle event payloads. SQLAlchemy sessions, repositories, PostgreSQL migrations, ownership constraints, and user/project authorization are still absent. The local database is development data and is not a production tenancy boundary.

Production prerequisite: add authenticated scoped repositories, a migration runner, connection health checks, transaction tests, and deployment-safe PostgreSQL persistence.
