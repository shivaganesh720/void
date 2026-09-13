# VOID API Reference

Current prefix: `/api/v1`

| Method | Endpoint                               | Purpose                                                       | Scope                                  |
| ------ | -------------------------------------- | ------------------------------------------------------------- | -------------------------------------- |
| GET    | `/health/live`                         | Liveness                                                      | None                                   |
| GET    | `/health/ready`                        | Readiness                                                     | None                                   |
| POST   | `/auth/register`                       | Create a local user account                                   | Public                                 |
| POST   | `/auth/login`                          | Issue a bearer access token                                   | Public                                 |
| GET    | `/auth/me`                             | Retrieve the current user                                     | Bearer token                           |
| POST   | `/auth/logout`                         | End the current local session                                 | Bearer token                           |
| PATCH  | `/auth/profile`                        | Save onboarding execution preferences                         | Bearer token                           |
| POST   | `/projects`                            | Create an owned project                                       | Bearer token                           |
| GET    | `/projects`                            | List owned/member projects                                    | Bearer token                           |
| POST   | `/missions/resume-jd`                  | Create and execute text Resume/JD mission                     | Client-supplied development project ID |
| POST   | `/missions/resume-jd/upload`           | Parse uploads and execute mission                             | Form project ID                        |
| GET    | `/missions?project_id=...`             | List missions; supports `status`, `search`, `limit`, `offset` | In-memory project filter               |
| GET    | `/missions/{id}?project_id=...`        | Retrieve mission detail, result, metadata, events             | In-memory project filter               |
| GET    | `/missions/{id}/tasks?project_id=...`  | Retrieve the current task                                     | In-memory project filter               |
| GET    | `/missions/{id}/events?project_id=...` | Retrieve lifecycle events                                     | In-memory project filter               |
| GET    | `/dashboard/summary?project_id=...`    | Counts and recent missions                                    | In-memory project filter               |

The local API uses bearer access tokens and project membership checks. Refresh-token rotation, durable sessions, and PostgreSQL-backed ownership are still deferred; do not treat this API as production-secure until those controls are connected.
