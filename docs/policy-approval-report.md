# Policy and Approval Report

`backend/app/control_plane/policy.py` and strategy helpers provide pure policy decisions and are unit tested. They are not connected to authenticated API execution, task dispatch, tool calls, provider calls, or durable audit records.

Approval requests, mission pause/resume around approval, decision persistence, duplicate decision prevention, and approval UI/API are not implemented. High-risk operations are unavailable because the corresponding execution gateways do not exist.
