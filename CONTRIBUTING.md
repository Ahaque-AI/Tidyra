# Contributing to Tidyra

Thanks for your interest. This document explains how to get set up, what
the conventions are, and how to submit changes.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Tidyra uses uv for everything: the
  Python runtime, dependency management, scripts, and tooling.
- A desktop with a graphical environment — Tidyra is a Flet desktop app.

## First-time setup

```powershell
git clone https://github.com/abdulhaque/tidyra.git
cd tidyra
uv sync --extra dev
uv run python -m tidyra        # smoke launch — the window should open
```

`uv sync --extra dev` installs the runtime deps (Flet, platformdirs) plus
the dev tools (ruff, mypy).

## Daily workflow

| Task | Command |
|---|---|
| Run the app | `uv run tidyra` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Type check | `uv run mypy src` |
| Add a runtime dep | `uv add <package>` |
| Add a dev tool | `uv add --dev <package>` |

Do not introduce `pip`, `requirements.txt`, or manual `python -m venv`
workflows. They are not supported.

## Project layout

```
src/tidyra/
  domain/          pure concepts — no Flet, no I/O
  application/     orchestration: scan → plan → execute
  infrastructure/  filesystem + TOML loader
  presentation/    Flet UI (thin; no business logic)
  resources/       built-in default rules
docs/              architecture, configuration, development, roadmap
```

The dependency direction is one-way:

```
presentation → application → domain ← infrastructure
```

The domain must never import from Flet, `pathlib` (for mutation), or
`tomllib`. If you find yourself wanting to import something in the
domain that touches the outside world, add a Protocol or callable to the
domain and let the application layer inject the implementation.

## Adding a rule

Open `src/tidyra/resources/default_rules.toml` and append a new
`[[rule]]` table. To override a built-in rule for yourself, copy the
file to your user config dir and edit it there — see
[`docs/configuration.md`](docs/configuration.md) for the path on each OS.

## Adding a strategy

A strategy turns `(root, entries, rules)` into an `OrganizationPlan`.
Create a new module under `src/tidyra/domain/strategies/`, implement the
`OrganizationStrategy` Protocol, and wire it into `OrganizeService` (or
add a separate service if it's optional). Strategies must be pure: no
filesystem I/O, no Flet, no logging side effects.

## Adding a view

1. Create `src/tidyra/presentation/views/<name>.py` with a
   `def <name>_view(app: TidyraApp) -> ft.Control:` function.
2. Add a `Screen` enum entry in `state.py` if the view is a new screen.
3. Wire the screen into `TidyraApp.render`.
4. Use `if TYPE_CHECKING:` for the `TidyraApp` import to avoid the
   circular dependency between views and the controller.

Views must be thin: hand off to the controller, render the returned
data, no logic.

## Submitting changes

1. Fork the repo and create a branch (`git checkout -b my-change`).
2. Make your change. Run `uv run ruff check .` and `uv run mypy src`
   before committing.
3. Commit with a clear subject. Conventional commits encouraged but
   not required.
4. Open a pull request describing the change, the motivation, and any
   screenshots for UI work.

## Release notes

Tidyra follows [Keep a Changelog](https://keepachangelog.com/) format
in [`CHANGELOG.md`](CHANGELOG.md).

## Code of conduct

Be respectful. We're all here to make a small, useful piece of software.
