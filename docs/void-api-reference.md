# VOID API Reference

Current prefix: `/api/v1`

| Method | Endpoint                               | Purpose                                                       | Scope                                  |
| ------ | -------------------------------------- | ------------------------------------------------------------- | -------------------------------------- |
| GET    | `/health/live`                         | Liveness                                                      | None                                   |
| GET    | `/health/ready`                        | Readiness                                                     | None                                   |
| POST   | `/missions/resume-jd`                  | Create and execute text Resume/JD mission                     | Client-supplied development project ID |
| POST   | `/missions/resume-jd/upload`           | Parse uploads and execute mission                             | Form project ID                        |
| GET    | `/missions?project_id=...`             | List missions; supports `status`, `search`, `limit`, `offset` | In-memory project filter               |
| GET    | `/missions/{id}?project_id=...`        | Retrieve mission detail, result, metadata, events             | In-memory project filter               |
| GET    | `/missions/{id}/tasks?project_id=...`  | Retrieve the current task                                     | In-memory project filter               |
| GET    | `/missions/{id}/events?project_id=...` | Retrieve lifecycle events                                     | In-memory project filter               |
| GET    | `/dashboard/summary?project_id=...`    | Counts and recent missions                                    | In-memory project filter               |

The API has no authentication middleware. Project IDs are therefore request parameters for the development slice, not an authorization mechanism. Do not treat this API as production-secure until identity and membership checks are connected.
