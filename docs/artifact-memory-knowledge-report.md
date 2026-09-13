# Artifact, Memory, and Knowledge Report

Artifacts have a disconnected SQLAlchemy model but no runtime storage, upload/download API, preview, versioning, retention, or ownership checks. Memory and knowledge/RAG have no runtime implementation, vector store, retrieval path, consent workflow, deletion path, or audit record.

The current upload path is transient parsing input for Resume/JD analysis, not artifact management. Synthetic local inputs are recommended; private resume retention is not supported.
