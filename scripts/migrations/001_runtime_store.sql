-- VOID local development migration 001
-- The application applies this schema idempotently through RuntimeStore.
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_missions_project_id ON missions(project_id);
CREATE INDEX IF NOT EXISTS ix_missions_updated_at ON missions(updated_at);
