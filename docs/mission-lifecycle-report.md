# Mission Lifecycle Report

Implemented states include `DRAFT`, `VALIDATING`, `PLANNED`, `APPROVED`, `RUNNING`, `COMPLETED`, `FAILED`, and `BLOCKED`, with transition validation in `backend/app/control_plane/state.py`. Mission events, task state, result, and timestamps are now persisted in the local SQLite runtime store.

`PAUSED`, `WAITING_FOR_APPROVAL`, `CANCELLING`, `CANCELLED`, and `EXPIRED` are represented by contracts but are not exposed as working controls. Retry, cancellation, duplicate execution prevention, actor checks, and background recovery remain unimplemented.
