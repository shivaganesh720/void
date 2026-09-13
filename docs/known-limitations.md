# Known Limitations

- Authentication and authorization are not implemented.
- Project IDs are client-supplied development filters, not access control.
- Mission/task/event/result data is in process memory and resets on restart.
- Resume/JD execution is synchronous and deterministic; no external model provider is called.
- No worker, scheduler, queue, retry, timeout, pause, resume, cancel, or approval service exists.
- No durable artifacts, settings, memory, knowledge, workflow, evaluation, agent, capability, model, or tool registry exists.
- No browser E2E test runner is configured.
- The existing frontend lint script is incompatible with the installed Next.js version.
