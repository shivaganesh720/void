# VOID Pending Implementation Plan

## P0: production boundary

1. Add an authenticated identity/session boundary and derive project access server-side.
2. Connect SQLAlchemy sessions, migrations, repositories, and transaction handling.
3. Move mission/task/events/results into durable project-scoped tables.
4. Define a queue/worker contract before adding asynchronous execution.
5. Add integration tests against the configured database and authorization matrix.

## P1: governed capabilities

1. Persist approval decisions and policy audit records.
2. Add artifact storage with content hashing, retention, and access checks.
3. Add registries for agents, capabilities, providers, and tools.
4. Add settings persistence with secret status masking.

## P2: extended product surfaces

Define and implement memory, workflows, evaluation, activity, profile, help, and execution-control surfaces only after their ownership and persistence contracts are specified.

No migration or database reset is performed by the current development slice.
