# Domain layer

The domain layer is the heart of Tidyra: dataclasses, enums, protocols, and pure functions. It is the only layer that has zero side effects and the only one whose tests do not need a filesystem, Flet, or TOML.

Start with [invariants/domain.md](invariants/domain.md). The rules there are short but absolute — the whole "engine is replaceable" promise rides on them.

- [Invariants](invariants/index.md)
- [domain.md](invariants/domain.md)
- [Architecture](../../architecture.md) — the layer diagram and dependency direction.

## What's in the domain layer

```
src/tidyra/domain/
├── models.py        FileEntry
├── rules.py         OrganizationRule
├── plans.py         OrganizationPlan, FileOperation, SkipReason,
│                    PlanValidator, OrganizationResult
├── strategies.py    OrganizationStrategy Protocol, RuleBasedStrategy
└── (future)         LLMStrategy (Phase 3)
```

## How the layer fits

```
Flet Presentation
        ↓
Application Services
        ↓
Domain
        ↑
Infrastructure
```

Arrows never reverse. If a view wants to call domain logic, it goes through `application/services.py`. If the domain needs a path, scan, or `is_within` operation, it does so via a `FileSystem` Protocol that `infrastructure` implements.