# VOID API Reference

All API routes are prefixed with `/api/v1/`. Authentication is handled via Bearer Tokens (JWT).

## Authentication (`/api/v1/auth`)
- `POST /register`: Register a new user account.
- `POST /login`: Authenticate and receive a JWT token.
- `GET /me`: Retrieve the authenticated user's profile.
- `PATCH /profile`: Update user preferences (e.g., AI awareness, default mode).

## Projects (`/api/v1/projects`)
- `GET /`: List all projects for the authenticated user.
- `POST /`: Create a new workspace project.

## Missions (`/api/v1/missions`)
- `GET /`: List missions scoped to a specific `project_id`.
- `GET /{mission_id}`: Retrieve detailed mission metadata.
- `GET /{mission_id}/tasks`: List all tasks associated with a mission.
- `GET /{mission_id}/events`: List all audit and execution events for a mission.
- `GET /{mission_id}/explanation-report`: Generate a detailed breakdown of mission execution.
- `POST /resume-jd`: Launch a new Resume-JD analysis mission.

## Approvals (`/api/v1/approvals`)
- `GET /`: List pending manual approvals.
- `POST /{approval_id}/grant`: Grant execution permission.
- `POST /{approval_id}/deny`: Deny execution permission.

## Gateways (`/api/v1/gateways`)
- `GET /tools`: List all registered tools in the `SafeToolGateway`.
- `GET /models`: List all available models in the `ModelGateway`.

## Knowledge & Memory (`/api/v1/projects/{project_id}`)
- `GET /knowledge`: List project-scoped RAG knowledge documents.
- `GET /memory`: List project-scoped key-value memories.
- `POST /memory`: Create a new memory entry.

## Workflows (`/api/v1/workflows`)
- `GET /`: List registered workflows in the system.
- `GET /{workflow_id}`: Get workflow details.
- `GET /{workflow_id}/versions`: Get version history for a workflow.

## Admin (`/api/v1/admin`)
- *(Requires `ADMIN` role)*
- `GET /overview`: Platform-wide usage statistics.
- `GET /users`: List all platform users.

## Real-time Events
- `WS /api/v1/ws/missions/{mission_id}`: WebSocket endpoint for streaming real-time mission execution events.
