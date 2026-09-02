# Architecture

Tidyra is structured as four layers with one-way dependencies. The
boundaries exist so that each layer can be understood, tested, and
changed without dragging the others with it.

## Layer diagram

```
┌──────────────────────────────────────────────┐
│            Flet Presentation                 │
│  (views, components, UIState, controller)    │
└──────────────────┬───────────────────────────┘
                   │ depends on
                   ▼
┌──────────────────────────────────────────────┐
│            Application Services              │
│  (OrganizeService, OrganizeExecutor,         │
│   scan_directory)                            │
└──────────────────┬───────────────────────────┘
                   │ depends on
                   ▼
┌──────────────────────────────────────────────┐
│            Domain                            │
│  (FileEntry, OrganizationRule, Organization-  │
│   Plan, PlanValidator, OrganizationStrategy, │
│   RuleBasedStrategy)                         │
└──────────────────▲───────────────────────────┘
                   │ implemented by
                   │
┌──────────────────────────────────────────────┐
│            Infrastructure                    │
│  (LocalFileSystem, ConfigService, default    │
│   rules TOML)                                │
└──────────────────────────────────────────────┘
```

## Dependency direction

- **Presentation** knows about application services (calls
  ``OrganizeService``). It does not know about infrastructure or domain
  internals.
- **Application** knows about the domain and orchestrates it. It asks
  the infrastructure layer (via ``FileSystem`` and ``ConfigService``
  injected in) to do real work.
- **Domain** knows only about itself. It contains dataclasses, enums,
  protocols, and pure functions. It imports nothing from Flet,
  ``tomllib``, or the filesystem.
- **Infrastructure** implements domain-level Protocols
  (``FileSystem``) and provides real I/O. It depends on the domain
  types but not on the application or presentation.

The arrows never reverse. If you find yourself wanting to import
something "upward" — for example, importing a Flet widget into the
domain — that's a signal to add a Protocol in the domain and inject the
implementation.

## The central concept: ``OrganizationPlan``

Every meaningful interaction with the user's files goes through one
artifact: an ``OrganizationPlan``.

```
scan → propose → validate → preview → confirm → execute
                    │
                    └── OrganizationPlan
                          ├── to_execute() → moved by executor
                          └── skipped()    → shown in preview, ignored
```

The plan is produced by a strategy and validated by ``PlanValidator``.
The same plan is shown to the user in the preview and consumed by the
executor. There is no second, independently-calculated UI view of "what
will happen" — the preview is the plan.

This is the foundation that lets a future ``LLMStrategy`` slot in
without changing the executor or the UI.

## Strategy abstraction

```python
class OrganizationStrategy(Protocol):
    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan: ...
```

A strategy is a pure function from inputs to a plan. The current
release ships ``RuleBasedStrategy``; a future ``LLMStrategy`` will
satisfy the same protocol.

```
OrganizationStrategy
        ├── RuleBasedStrategy    (this release)
        └── LLMStrategy          (future)
                │
                │ uses an LLM to decide
                │ "vacation.jpg → Images/" instead of relying on
                │ the .jpg extension
                │
                └── still returns an OrganizationPlan
                        │
                        └── same validator
                                │
                                └── same executor
```

The LLM never touches the filesystem. It returns a plan; the executor
applies it.

## Filesystem abstraction

```python
class FileSystem(Protocol):
    def scan(self, root: Path) -> Sequence[FileOperation]: ...
    def move(self, source: Path, destination: Path) -> None: ...
    def exists(self, path: Path) -> bool: ...
    def create_directory(self, path: Path) -> None: ...
    def is_within(self, path: Path, root: Path) -> bool: ...
```

Tests can inject an in-memory implementation without touching real
files. The production implementation is ``LocalFileSystem``.

## Safety guarantees

Enforced in ``PlanValidator``:

1. Never delete. Move only.
2. Source must be a regular file inside ``root``.
3. Destination must resolve inside ``root``.
4. Reject symlink sources.
5. Reject moves where the destination already exists.
6. Drop no-op moves.
7. Reject destinations that nest under another destination (recursive
   re-org guard).

Every rejected operation appears in the plan with a ``SkipReason``. The
preview shows it; the executor skips it. There is no silent overwrite.

## What's deliberately not here

- No CLI flag parser. The initial release is desktop-only.
- No undo. Future work (Phase 2).
- No background scheduler. Future work (Phase 4).
- No rule editor UI. Editing the TOML is the rule editor.
- No telemetry, no analytics, no network calls.

See [`roadmap.md`](../processes/roadmap.md) for what comes next.
