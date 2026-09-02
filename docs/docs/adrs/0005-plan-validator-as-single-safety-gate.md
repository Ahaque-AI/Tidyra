# ADR-0005: `PlanValidator` as the single safety gate

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra moves real files. Safety rules scattered between the executor and the strategy would drift from what the preview UI shows, and the user would see one plan while the executor enforces another.

## Decision

`PlanValidator` is the single source of safety. The seven guarantees — no delete, source must be a regular file, destination must resolve inside `root`, no symlink following, no silent overwrite, drop no-op moves, no nested destinations — are enforced exactly once, in `PlanValidator`. Every rejected operation appears in the plan with a `SkipReason`. The preview UI consumes the same `OrganizationPlan` the executor does.

The executor does not run safety checks. If a guarantee changes, it changes in the validator and in the [architecture.md safety-guarantees list](../domain/architecture.md#safety-guarantees) in the same change.

## Consequences

- Positive: the preview and the executor can never diverge.
- Positive: every guarantee has exactly one place to review in code review.
- Positive: a future `LLMStrategy` automatically inherits the same safety net.
- Negative: the validator concentrates logic that could be split. The split is documented in [domain/invariants/domain.md §5](../domain/invariants/domain.md#5-planvalidator-is-the-only-safety-gate).
- Follow-ups: any new safety check is added to `PlanValidator` plus the architecture doc. Adding it elsewhere is a regression.