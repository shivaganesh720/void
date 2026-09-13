# Resume/JD Intelligence Workflow

```mermaid
flowchart LR
  A[Upload] --> B[Parse]
  B --> C[Mission Creation]
  C --> D[Work Graph / Task State]
  D --> E[Agent Cells]
  E --> F[Model Gateway]
  F --> G[Validation]
  G --> H[Persistence]
  H --> I[Structured UI Result]
```

In the current slice, the analysis cell is a bounded local service and the Model Gateway stage is not configured. Parse failures stop before analysis. Validation failures stop completion. The API returns safe error codes instead of stack traces.
