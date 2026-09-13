# VOID Specification

## Product rule

The user chooses what. The user may choose how. If the user does not choose how, VOID selects how under governance.

## Execution modes

- AUTO: VOID selects a permitted strategy.
- GUIDED: VOID proposes a strategy and freezes the approved profile.
- MANUAL: the user selects permitted options, but backend policy still validates every choice.

## V1 vertical slice

Resume/JD intelligence should accept one resume and one job description as PDF with extractable text, DOCX, plain text, or Markdown. It should reject unsafe, oversized, empty, corrupt, unsupported, and scanned files.

The workflow should extract text, normalize skills, compare requirements, attach source evidence, distinguish facts from inferences and recommendations, validate output, generate a Markdown report, store an artifact hash, and persist an audit receipt.

## Required lifecycle states

Mission states: DRAFT, VALIDATING, PLANNED, WAITING_FOR_APPROVAL, APPROVED, RUNNING, PAUSED, CANCELLING, CANCELLED, COMPLETED, FAILED, BLOCKED, EXPIRED.

Task states: CREATED, READY, QUEUED, RUNNING, WAITING, RETRYING, SUCCEEDED, FAILED, CANCELLED, BLOCKED, TIMED_OUT.

## Required control components

Intent Gate, Mission Kernel, Execution Profile, Capability Registry, Capability Broker, Strategy Resolver, Mission Blueprint, Policy Engine, Approval Controller, Task State Service, Model Gateway, Tool Gateway, Agent Harness, Validator, Artifact Store, and Audit Store.

## Non-goals for the first implementation

OCR, RAG, web search, browser automation, email, calendar, CRM, shell execution, arbitrary code execution, computer control, external side effects, unrestricted internet, user-created agents, dynamic unrestricted workflows, and uncontrolled agent swarms.

## Completion rule

A feature is complete only when it is implemented, executable, tested, verified, documented, and compliant with architecture and security requirements. The current repository is partial and must not claim V1 completion.
