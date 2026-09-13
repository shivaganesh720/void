# VOID Known Limitations

- Missions, events, tasks, and analysis results are process memory only.
- There is no authentication or server-enforced project membership.
- Resume/JD execution is synchronous in the API process; there is no queue, lease, worker, retry, timeout, or cancellation service.
- The analyzer is deterministic and lexical. It does not call an external AI model and cannot verify experience, education, visual formatting, or claims beyond extracted text.
- Artifacts, settings, approvals, model providers, agents, capabilities, tools, memory, workflows, evaluation, and activity persistence are not implemented.
- The frontend is a single-page hash navigation shell rather than separate protected routes.
- `npm run lint` requires a script update because `next lint` is unsupported by the installed Next.js release.
