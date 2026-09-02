# Development

How to set up your environment, run the app, and contribute code.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Tidyra uses uv for everything.

`uv` brings its own Python interpreter and manages the virtualenv. You
do **not** need to install Python separately.

## Setup

```powershell
git clone https://github.com/abdulhaque/tidyra.git
cd tidyra
uv sync --extra dev
```

This installs:
- Runtime deps (`flet`, `platformdirs`)
- Dev tools (`ruff`, `mypy`)

## Common commands

| Task | Command |
|---|---|
| Run the app | `uv run tidyra` |
| Run as module | `uv run python -m tidyra` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Format check (CI) | `uv run ruff format --check .` |
| Type check | `uv run mypy src` |
| Add a runtime dep | `uv add <package>` |
| Add a dev tool | `uv add --dev <package>` |
| Re-lock deps | `uv lock` |
| Verbose logs | `$env:TIDYRA_LOG_LEVEL='DEBUG'; uv run tidyra` |
| JSON file log | `$env:TIDYRA_LOG_FILE='C:\Users\You\tidyra.jsonl'; uv run tidyra` |

## Project structure

```
src/tidyra/
  __init__.py
  __main__.py
  domain/
    models.py        FileEntry
    rules.py         OrganizationRule
    plans.py         OrganizationPlan, FileOperation, SkipReason,
                     PlanValidator, OrganizationResult
    strategies.py    OrganizationStrategy Protocol,
                     RuleBasedStrategy
  application/
    scanner.py       scan_directory
    services.py      OrganizeService
    organize.py      OrganizeExecutor
  infrastructure/
    filesystem.py    FileSystem Protocol, LocalFileSystem
    configuration.py ConfigService, default rule discovery
    logging.py       configure_logging (loguru sinks)
  presentation/
    app.py           Flet entry point (main, run)
    controller.py    TidyraApp
    state.py         UIState, Screen enum
    views/           home, preview, results
    components/      folder_picker, file_list, plan_view, result_view
  resources/
    default_rules.toml
docs/
  architecture.md
  configuration.md
  development.md  ← this file
  roadmap.md
```

## Adding a rule

1. Open `src/tidyra/resources/default_rules.toml`.
2. Append a `[[rule]]` table with at minimum `name` and `destination`.

That's it. To override or extend locally instead of shipping:

1. Copy `default_rules.toml` to your user config dir
   (`uv run python -c "from tidyra.infrastructure.configuration import get_config_service; print(get_config_service().default_config_path())"`
   to see the path).
2. Edit the copy.

User rules override defaults by `name`. See
[`configuration.md`](configuration.md).

## Adding a strategy

A strategy is anything that turns `(root, entries, rules)` into an
`OrganizationPlan`. The interface lives in
`src/tidyra/domain/strategies.py`:

```python
class OrganizationStrategy(Protocol):
    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan: ...
```

To add one:

1. Create a new module under `src/tidyra/domain/strategies/`.
2. Define a class that satisfies the protocol.
3. Wire it into `OrganizeService` (or add a constructor flag) in
   `src/tidyra/application/services.py`.

Strategies must be pure. No filesystem I/O, no Flet, no side effects
beyond returning the plan.

## Adding a view

1. Create `src/tidyra/presentation/views/<name>.py`:

   ```python
   from __future__ import annotations
   from typing import TYPE_CHECKING
   import flet as ft

   if TYPE_CHECKING:
       from tidyra.presentation.controller import TidyraApp


   def <name>_view(app: TidyraApp) -> ft.Control:
       return ft.Container(content=ft.Text("<name>"))
   ```

2. If it's a new screen, add an entry to `Screen` in
   `src/tidyra/presentation/state.py`.
3. Add a branch to `TidyraApp.render` in
   `src/tidyra/presentation/controller.py`.

Use `TYPE_CHECKING` for the controller import — the views and the
controller would otherwise form a circular import.

## Adding a component

Components are reusable Flet controls under
`src/tidyra/presentation/components/`. Each is a function that returns
a `ft.Control`. They take callbacks for events rather than importing
the controller, to keep them easy to test.

## Adding a config field

If you add a field to `OrganizationRule` (in
`src/tidyra/domain/rules.py`), also update:

- `_rule_from_dict` in `src/tidyra/infrastructure/configuration.py` so
  the field is parsed from TOML.
- `default_rules.toml` to document the field.
- This doc and [`configuration.md`](configuration.md).

## Code conventions

- Type hints everywhere. mypy strict is enforced.
- No business logic in Flet event handlers — they call the controller.
- No `os` module — use `pathlib`.
- No raw TOML in domain code — only `OrganizationRule` dataclasses.
- One concern per module. If a module exceeds ~300 lines, split it.

## Logging

Tidyra uses [`loguru`](https://loguru.readthedocs.io/) for structured
logging. Configuration lives in `src/tidyra/infrastructure/logging.py`
and is invoked once at process start (in `run()` and `__main__.py`).
Every other module imports `from loguru import logger` and uses
`logger.bind(...)` for structured context.

Records are emitted as colourised lines on `stderr` by default. Set
`TIDYRA_LOG_FILE` to mirror the same records to a JSON-lines file
(rotated at 10 MB, last 5 retained) for downstream tooling.

| Env var | Purpose | Default |
|---|---|---|
| `TIDYRA_LOG_LEVEL` | Console + file sink level | `INFO` |
| `TIDYRA_LOG_FILE` | Path for the JSON-lines mirror | unset (file sink disabled) |

Examples:

```powershell
$env:TIDYRA_LOG_LEVEL='DEBUG'; uv run tidyra
$env:TIDYRA_LOG_FILE="$env:USERPROFILE\tidyra.jsonl"; uv run tidyra
```

Structured fields that every record carries:

- `record.extra.component` — the subsystem that emitted the record
  (`executor`, `controller`, `filesystem`, `config`, `service`,
  `logging`, `presentation`).
- Per-call bindings — `root`, `file_path`, `rule_name`, `skip_reason`,
  `moves`, `failed`, etc., depending on the call site.

When something goes wrong, prefer `logger.exception("...")` inside an
`except` block — loguru captures the traceback automatically and the
JSON record carries a populated `record.exception` object with `type`,
`value`, and `traceback`.

## Smoke-testing a change

After any change:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run tidyra
```

The Flet window should open without errors. Pick a folder you don't
mind moving files from, scan it, and verify the preview matches your
expectations.

## Release process

1. Bump version in `pyproject.toml`.
2. Move `[Unreleased]` items in `CHANGELOG.md` to a dated section.
3. Tag and push. CI builds and publishes (when CI exists).
