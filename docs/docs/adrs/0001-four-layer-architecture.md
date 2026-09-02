# ADR-0001: Four-layer architecture

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra needs a layer split that keeps the engine testable without launching a UI and lets a future `LLMStrategy` slot in without rewriting the executor.

## Decision

Tidyra is split into four layers with one-way dependencies:

```
Flet Presentation
        ↓
Application Services
        ↓
Domain
        ↑
Infrastructure
```

- **Presentation** knows about application services. No infrastructure, no domain internals.
- **Application** orchestrates scanning, classifying, planning, executing. Asks infrastructure (via injected Protocols) to do real work.
- **Domain** knows only about itself. Pure dataclasses, enums, protocols, and pure functions.
- **Infrastructure** implements domain Protocols (`FileSystem`, `ConfigService`). It depends on the domain types but not on the application or presentation.

## Consequences

- Positive: domain can be tested without UI, filesystem, or TOML.
- Positive: a future `LLMStrategy` satisfies the existing `OrganizationStrategy` Protocol and reuses every other layer.
- Positive: every dependency has one direction; the boundary is enforceable in code review.
- Negative: cross-cutting changes (logging, error handling) must be added at the appropriate layer rather than reaching "upward" or "downward".
- Follow-ups: every new module must declare its layer in its location under `src/tidyra/`. The four-layer diagram lives in `docs/docs/domain/architecture.md`.