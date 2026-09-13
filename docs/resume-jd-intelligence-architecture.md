# Resume/JD Intelligence Architecture

The presentation layer submits either text or two files. The API validates the request and upload metadata, parses untrusted document content, creates a project-scoped mission record, applies the existing lifecycle transition guard, runs the bounded analysis service, validates the result, and stores the result in the current development store.

The analyzer is deterministic and evidence-backed. It recognizes a bounded skill vocabulary and labels source terms; it does not invent experience, education, projects, metrics, or certifications. External model calls are intentionally absent because no Model Gateway or provider configuration exists in this repository.

Production boundaries still required: authenticated identity, project authorization, durable storage, retention/deletion policy, scheduler/work graph persistence, and a provider-neutral model gateway.
