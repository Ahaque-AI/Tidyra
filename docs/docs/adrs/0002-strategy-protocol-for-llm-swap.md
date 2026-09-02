# ADR-0002: `OrganizationStrategy` Protocol with future LLM slot

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: The roadmap's Phase 3 introduces an LLM-driven classifier. We want to ship the engine contract in Phase 1 without committing to the LLM implementation, so that the swap-in is additive.

## Decision

The engine is one implementation of an `OrganizationStrategy` Protocol. Both `RuleBasedStrategy` (Phase 1) and a future `LLMStrategy` (Phase 3) produce the same `OrganizationPlan`:

```python
class OrganizationStrategy(Protocol):
    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan: ...
```

The LLM never touches the filesystem directly. It returns a plan; the executor applies it. The preview UI consumes the same plan that the executor consumes.

## Consequences

- Positive: the strategy abstraction is the central seam. `LLMStrategy` will not require changes to the executor, the validator, or the UI.
- Positive: strategies are pure functions — easy to unit-test with synthetic entries and rules.
- Negative: the Protocol shape must be stable across versions; renaming a method is breaking.
- Negative: cross-cutting concerns (rate limiting, cost tracking) live at the strategy implementation, not the Protocol.
- Follow-ups: when `LLMStrategy` lands, capture the choices (model, provider, prompt format, fallback) in a new ADR.