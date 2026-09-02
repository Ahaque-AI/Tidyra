# Domain layer rules

The domain layer is pure Python. Everything in this file is enforced by code review and the `mypy --strict` check in CI.

## 1. Zero side effects

The domain layer MUST NOT import:

- `flet`, `flet.*`, any UI library
- `tomllib`, `tomli`, `tomli_w`, `yaml`, any config parser
- `os`, `subprocess`, `shutil`, anything that mutates real state
- `logging` (use `loguru` only in application + infrastructure; domain code returns data and lets the caller log)

If a domain module needs a side effect, add a Protocol in `domain/` and inject the implementation from `infrastructure/`. The domain does not know which implementation it gets.

## 2. Frozen dataclasses only

Domain types are `@dataclass(frozen=True)`. No `__post_init__` mutation, no `field(default_factory=...)` for stateful values, no `__eq__` overrides. Identity is value identity.

## 3. `Path` is data, not I/O

`pathlib.Path` may appear in domain types (e.g. `FileEntry.path`, `OrganizationPlan.root`), but no method on those Paths may be called from domain code. Reading metadata is fine; mutating the filesystem is not. The boundary is "do not call `.mkdir`, `.rename`, `.unlink`, `.open`".

## 4. Strategies satisfy the Protocol

```python
class OrganizationStrategy(Protocol):
    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan: ...
```

A strategy is a pure function. Same inputs → same plan. No randomness, no wall-clock dependency, no logging, no I/O. Strategies live under `src/tidyra/domain/` — never under `infrastructure/`.

## 5. `PlanValidator` is the only safety gate

Every operation that touches the filesystem goes through `PlanValidator`. Adding a new safety check means adding it to the validator and to the [architecture doc](../../architecture.md) "Safety guarantees" list in the same change. Do not sprinkle `if` checks in the executor; the plan must already say "skip" or "execute".

## 6. `OrganizationPlan` is the contract between layers

The preview UI and the executor both consume `OrganizationPlan`. There is no second "what will happen" calculation in the UI. If the preview shows something, the executor will do exactly that — no silent divergence.

## 7. Naming

- Public dataclass fields are nouns.
- `SkipReason` enum members are `SCREAMING_SNAKE_CASE` and their values are stable string literals (the wire format). Never rename a value without an ADR.
- Strategy classes end in `Strategy` (`RuleBasedStrategy`, `LLMStrategy`).

## 8. One concern per module

If a module exceeds ~300 lines it has too many types. Split it. A common split is `models.py`, `rules.py`, `plans.py`, `strategies.py` — keep that pattern unless a future split earns its place with an ADR.

## 9. Tests are the user's responsibility

Tidyra ships with `FakeFileSystem` and protocol seams but no test scaffolding. Add an ADR if you intend to introduce `pytest` or a similar runner. Domain code is structured so that `FakeFileSystem` lets you drive the whole stack from a test without I/O — keep that property when adding new code.