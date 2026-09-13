# VOID End-to-End Workflow

## Current verified path

```text
Browser
  -> Next.js client shell
  -> FastAPI request contract
  -> upload validation / text validation
  -> in-memory mission + task creation
  -> lifecycle transitions: DRAFT -> VALIDATING -> PLANNED -> APPROVED -> RUNNING
  -> parsing and deterministic Resume/JD analysis
  -> structured result validation
  -> task SUCCEEDED and mission COMPLETED
  -> mission result, events, and dashboard summary
```

Text uses `POST /api/v1/missions/resume-jd`; files use `POST /api/v1/missions/resume-jd/upload`. Detail, task, event, list, and dashboard reads are project-filtered in memory. The UI refreshes mission data while a mission is non-terminal, although the current execution is synchronous.

## Failure path

Invalid uploads return `422` with a safe actionable message. Workflow exceptions are logged with mission/task IDs and returned as generic failure state; stack traces are not sent in normal responses. There is no provider, timeout, rate-limit, network, worker, retry, cancellation, or WebSocket path to verify.

## Future path

Identity must establish project membership before request scoping. Then repositories and migrations should persist missions, tasks, events, and results. A worker contract should define leases, retries, timeouts, cancellation, and correlation before asynchronous execution is introduced.
