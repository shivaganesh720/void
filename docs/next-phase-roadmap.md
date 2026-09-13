# VOID Next-Phase Roadmap

## Priority 0

1. Add authentication and server-derived project membership.
2. Connect SQLAlchemy engine/session wiring and safe migrations.
3. Add repositories for projects, missions, tasks, events, and results.
4. Add integration tests for transactions and cross-project access.

## Priority 1

1. Define queue/worker/lease/retry/timeout semantics.
2. Persist audit events and artifacts with access controls.
3. Connect policy decisions to authenticated API execution.
4. Add browser E2E testing and replace the invalid lint script with a supported lint configuration.

## Priority 2

1. Implement settings and approval services.
2. Add agent, capability, model/provider, and tool registries.
3. Add governed gateways and provider failure handling.

## Priority 3

Implement memory, knowledge, workflows, evaluation, activity, profile, help, and advanced execution controls only after their storage and authorization contracts are defined.
