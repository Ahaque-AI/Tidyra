# Tidyra — Design Spec

**Date:** 2026-09-02
**Status:** Approved (with one revision — testing deferred to user)
**Author:** Brainstorming session between Abdul Haque and Mavis

## Goal

A small, safe, deterministic, rule-based desktop folder organizer. The user picks a directory (typically `~/Downloads`), the app scans it, classifies files with configurable rules, produces an `OrganizationPlan`, previews the plan, and only moves files after explicit user confirmation.

Long-term the engine must be replaceable with an LLM-driven strategy that produces the same `OrganizationPlan` shape — but no LLM code is shipped in this initial release.

## Non-goals (this release)

- Web frontend, API server, database, authentication, cloud, telemetry.
- File deletion (move only).
- LLM strategy implementation (interface only).
- Background scheduling.
- Undo / history.
- A custom rule editor UI (config file editing only).
- Automated test scaffolding (handled manually by the user).

## Stack & dependencies

| Layer | Choice |
|---|---|
| Package/runtime | `uv` (mandatory; `pyproject.toml` + `uv.lock`) |
| UI | `flet` |
| Domain | stdlib only (`dataclasses`, `enum`, `pathlib`, `tomllib`) |
| Config dir | `platformdirs` (cross-platform user config dir) |
| Lint/format | `ruff` (lint + format) |
| Type check | `mypy` (strict) |

Python requirement: **≥3.11** (so `tomllib` is stdlib).

No `pip`, no `requirements.txt`, no PyYAML, no test runner, no HTTP, no DB.

## Package layout

```
tidyra/
├── pyproject.toml
├── uv.lock
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── src/tidyra/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── rules.py
│   │   ├── plans.py
│   │   └── strategies.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── organize.py
│   │   ├── scanner.py
│   │   └── services.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── filesystem.py
│   │   └── configuration.py
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── state.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── home.py
│   │   │   ├── preview.py
│   │   │   └── results.py
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── folder_picker.py
│   │       ├── file_list.py
│   │       ├── plan_view.py
│   │       └── result_view.py
│   └── resources/
│       └── default_rules.toml
└── docs/
    ├── architecture.md
    ├── configuration.md
    ├── development.md
    └── roadmap.md
```

Entry point: `tidyra = "tidyra.presentation.app:main"` — `uv run tidyra` launches the Flet desktop app.

## Architecture

Dependency direction (one-way, top to bottom):

```
Flet Presentation
        ↓
Application Services
        ↓
Domain
        ↑
Infrastructure
```

- **Domain** knows nothing about Flet, `tomllib`, or real paths beyond `pathlib`.
- **Application** orchestrates scanning → classifying → planning → executing.
- **Infrastructure** is the only layer that talks to the filesystem or loads TOML.
- **Presentation** wires Flet controls to application services. No business logic in handlers.

This lets the organizer engine be tested without launching a UI, and lets a future `LLMStrategy` be swapped in without touching the executor.

## Domain model

```python
# domain/models.py
@dataclass(frozen=True)
class FileEntry:
    path: Path
    name: str
    extension: str
    size: int
    is_symlink: bool
    is_directory: bool


# domain/rules.py
@dataclass(frozen=True)
class OrganizationRule:
    name: str
    destination: str  # relative to root
    extensions: frozenset[str]
    patterns: tuple[str, ...]  # reserved for future glob support
    priority: int  # higher wins on conflict


# domain/plans.py
@dataclass(frozen=True)
class SkipReason(enum.Enum):
    UNMATCHED = "unmatched"
    SYMLINK = "symlink"
    NOT_A_FILE = "not_a_file"
    OUTSIDE_ROOT = "outside_root"
    RULE_CONFLICT = "rule_conflict"
    DESTINATION_EXISTS = "destination_exists"
    NO_OP = "no_op"
    NESTED_DESTINATION = "nested_destination"


@dataclass(frozen=True)
class FileOperation:
    source: Path
    destination: Path
    rule_name: str | None
    skip_reason: SkipReason | None  # None means "execute this"


@dataclass(frozen=True)
class OrganizationPlan:
    root: Path
    operations: tuple[FileOperation, ...]

    def to_execute(self) -> tuple[FileOperation, ...]: ...
    def skipped(self) -> tuple[FileOperation, ...]: ...


# domain/strategies.py
class OrganizationStrategy(Protocol):
    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan: ...
```

`PlanValidator` produces a fully annotated `OrganizationPlan` (some `FileOperation`s are executable, others are skipped with a `SkipReason`). Both the preview UI and the executor consume the **same** plan — dry-run and execute never diverge.

## Strategy & rule engine

- `RuleBasedStrategy` is the only implementation in this release.
- Rules ordered by `priority` descending, then declared order. The first matching rule wins. If two rules at the same priority both match the same file, the file gets `skip_reason=RULE_CONFLICT`.
- Files matching no rule get `skip_reason=UNMATCHED`. They appear in the preview so the user can see them, but the executor skips them.
- A catch-all rule (`Other → Misc/`) is the only built-in rule with a low priority that intentionally matches everything — so unmatched files are visible in the preview, never silently dropped.

Future `LLMStrategy` will satisfy the same `OrganizationStrategy` Protocol and produce the same `OrganizationPlan`. It will never touch the filesystem directly.

## Filesystem abstraction

```python
# infrastructure/filesystem.py
class FileSystem(Protocol):
    def scan(self, root: Path) -> Sequence[FileEntry]: ...
    def move(self, source: Path, destination: Path) -> None: ...
    def exists(self, path: Path) -> bool: ...
    def create_directory(self, path: Path) -> None: ...
    def is_within(self, path: Path, root: Path) -> bool: ...
```

`LocalFileSystem` (using `pathlib`) is the only concrete implementation in this release. Tests use a `FakeFileSystem` (in-memory) — testing is the user's responsibility, but the seams are in place.

Symlinks are recorded as `is_symlink=True` but never followed. The validator drops them with `skip_reason=SYMLINK`.

## Safety guarantees

Enforced in `PlanValidator`. The same plan goes to preview and execution, so what the user sees is what the filesystem gets.

1. Never delete. Move only.
2. Source must be a regular file inside `root`.
3. Destination must resolve inside `root` (no `..` escapes).
4. Reject symlink sources.
5. Reject moves where the destination already exists (no silent overwrite).
6. Drop no-op moves (`source == destination`).
7. Reject nested destinations (a destination under another destination's path — protects against recursive re-org in a single run).
8. Every rejected/skipped operation appears in the plan with a `SkipReason`; preview shows it; executor skips it.

## Configuration

- **Format:** TOML (stdlib `tomllib`).
- **Discovery order** (first wins; later layers are ignored):
  1. User config dir: `platformdirs.user_config_path("tidyra") / "rules.toml"`
  2. CWD: `./rules.toml`
  3. Built-in defaults shipped at `src/tidyra/resources/default_rules.toml`
- **Built-in default rules:**
  - Images → `Images/` (`.jpg .jpeg .png .webp .gif .bmp .tiff .svg`)
  - Documents → `Documents/` (`.pdf .docx .txt .xlsx .pptx .odt .md .rtf`)
  - Music → `Music/` (`.mp3 .wav .flac .aac .ogg .m4a`)
  - Videos → `Videos/` (`.mp4 .mkv .mov .avi .webm .wmv`)
  - Archives → `Archives/` (`.zip .tar .gz .bz2 .7z .rar .xz`)
  - Applications → `Applications/` (`.exe .msi .dmg .pkg .deb .rpm .apk`)
  - Other (catch-all) → `Misc/` (priority 0, no extensions)
- **Schema:**
  ```toml
  [[rule]]
  name = "images"
  destination = "Images"
  extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
  priority = 10
  ```
- **Loading:** `ConfigService.load()` returns `Sequence[OrganizationRule]`. User rules override defaults by `name`. Domain code never sees TOML types — only `OrganizationRule` dataclasses.

## UI flow (Flet, thin)

```
┌─ home ──────────────┐   ┌─ preview ──────────┐   ┌─ results ─────────┐
│ Pick folder         │ → │ Plan summary       │ → │ Done summary      │
│ [folder_picker]     │   │ [plan_view]        │   │ [result_view]     │
│ [Scan] → loading…   │   │ Will move N files  │   │ Moved N           │
│ File list preview   │   │ Skipped M (reasons)│   │ Skipped M         │
│                     │   │ [Organize] [Back]  │   │ [Done] [Back]     │
└─────────────────────┘   └────────────────────┘   └───────────────────┘
```

`presentation/state.UIState` holds view-local state (current screen, loading flag, error message, selected folder). Domain objects (plan, operations) flow through unchanged. Flet event handlers call `OrganizeService` and update `UIState` — no logic in handlers.

## Documentation

- `README.md` — public GitHub-ready: name, problem, features, safety, install (`uv`), run (`uv run tidyra`), configuration example, development, architecture link, roadmap link, contributing, license.
- `docs/architecture.md` — layer diagram, dependency direction, strategy abstraction, why LLM emits a plan.
- `docs/configuration.md` — TOML schema, locations, precedence, built-in defaults, conflict semantics.
- `docs/development.md` — uv workflow, adding a rule, adding a strategy, adding a view.
- `docs/roadmap.md` — phases 1–4.

## Definition of Done

1. `pyproject.toml` is configured; `uv.lock` is generated.
2. `uv sync` succeeds.
3. Flet is installed and the app launches: `uv run tidyra` opens the window.
4. The presentation layer is thin — no business logic in Flet handlers.
5. Domain logic has zero Flet imports.
6. Application services orchestrate the workflow.
7. Filesystem access lives only behind `FileSystem`.
8. A folder can be picked through the UI.
9. Files can be scanned.
10. Rules can classify files.
11. An `OrganizationPlan` can be generated.
12. The plan displays in the Flet preview.
13. No file is moved until the user confirms.
14. Conflicts produce a `SkipReason` and never silently overwrite.
15. Built-in default rules are shipped as package data.
16. Ruff lint + format pass; mypy strict passes.
17. README, CONTRIBUTING, CHANGELOG, LICENSE, and the four docs files exist.
18. No LLM code is shipped.

Automated tests are intentionally out of scope for this release — the user will write them.

## Phased delivery

| Phase | In scope now | Out of scope |
|---|---|---|
| **1 — this release** | Scan, classify, plan, preview, safe move, TOML config, built-in defaults | Automated tests, undo, custom rule editor, LLM |
| 2 | — | Undo history, better conflict UI, custom rule editor |
| 3 | — | `LLMStrategy` |
| 4 | — | Background scheduling, integrations |

## Verification at the end

```powershell
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run tidyra        # smoke-launch
```
