# VOID Complete Architecture Status

VOID currently has a FastAPI boundary, deterministic control-plane modules, bounded document parsing, a synchronous Resume/JD workflow, an in-memory mission store, and a Next.js single-page shell.

The intended architecture remains: presentation -> API validation -> control plane -> bounded workflow -> validation -> persistence -> UI. The current runtime stops at an in-memory development persistence boundary. There is no authenticated actor context, database session, queue, worker, model gateway, tool gateway, agent harness, or durable audit stream.

The current implementation deliberately does not bypass policy or claim external model execution. See [void-feature-status-matrix.md](void-feature-status-matrix.md) for classifications.
