# Contributing to Tidyra

Thanks for your interest. This document explains how to get set up, what
the conventions are, how work flows through the repo, and how to submit
changes.

## How work flows

Tidyra uses a layered docs site to keep working rules discoverable.
Before doing anything in this repo, the agent (and you, when in doubt)
reads the rules. The full path:

```
AGENTS.md                       routing + meta rules (read first, <100 lines)
    ↓
docs/docs/index.md              knowledge domain map
    ↓
docs/docs/<domain>/index.md     domain entry
    ↓
docs/docs/<domain>/invariants/  rule docs for that domain
    ↓
source code                     ground truth — verify against the rule
    ↓
implementation
```

| If you are… | Start at |
|---|---|
| An agent or new contributor | [AGENTS.md](AGENTS.md) |
| Hunting for a rule by topic | [docs/docs/index.md](docs/docs/index.md) |
| Writing or reviewing an architectural decision | [docs/docs/processes/invariants/processes.md §1](docs/docs/processes/invariants/processes.md#1-architectural-decisions--adr) |
| Logging a bug fix or incident | [docs/docs/processes/invariants/processes.md §2](docs/docs/processes/invariants/processes.md#2-bug-fixes--fix-log) |

## Architectural decisions

Every decision that shapes the codebase — a new dependency, a layer boundary, a replacement for an existing pattern — gets an ADR under [`docs/docs/adrs/`](docs/docs/adrs/index.md). The agent drafts the ADR; you confirm the wording. The format and authoring rule are documented in [docs/docs/processes/invariants/processes.md §1](docs/docs/processes/invariants/processes.md#1-architectural-decisions--adr). The current roster is in [docs/docs/adrs/index.md](docs/docs/adrs/index.md).

If a change you make touches a public doc (README, configuration, etc.), update that doc in the same commit and link the ADR from any rule doc that codifies the lesson.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Tidyra uses uv for everything: the Python runtime, dependency management, scripts, and tooling.
- A desktop with a graphical environment — Tidyra is a Flet desktop app.

## First-time setup

```powershell
git clone https://github.com/abdulhaque/tidyra.git
cd tidyra
uv sync --extra dev
uv run python -m tidyra        # smoke launch — the window should open
```

`uv sync --extra dev` installs the runtime deps (Flet, platformdirs) plus the dev tools (ruff, mypy).

## Daily workflow

| Task | Command |
|---|---|
| Run the app | `uv run tidyra` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Type check | `uv run mypy src` |
| Add a runtime dep | `uv add <package>` |
| Add a dev tool | `uv add --dev <package>` |

Do not introduce `pip`, `requirements.txt`, or manual `python -m venv` workflows. They are not supported. See [ADR-0003](docs/docs/adrs/0003-uv-only-no-pip-no-venv.md).

## Project layout

```
src/tidyra/
  domain/          pure concepts — no Flet, no I/O
  application/     orchestration: scan → plan → execute
  infrastructure/  filesystem + TOML loader
  presentation/    Flet UI (thin; no business logic)
    brand.py       logo path resolver (single source of truth for the mark)
    views/         home, preview, results
    components/    folder_picker, file_list, plan_view, result_view
  resources/       built-in default rules + tidyra-logo.svg
docs/
  AGENTS.md        routing + meta rules (<100 lines)
  docs/            knowledge domain map and rule docs
    index.md       entry point
    core/          universal rules
    domain/        pure-Python layer
    frontend/      Flet presentation
    security/      filesystem safety, secrets
    tooling/       uv, ruff, mypy, packaging
    processes/     plans, ADRs, cadence, README, releases
    adrs/          architectural decision records
    known-issues/  fix logs
  plans/           step-by-step plans for features too large for a single conversation
```

The dependency direction is one-way:

```
presentation → application → domain ← infrastructure
```

The domain must never import from Flet, `pathlib` (for mutation), or `tomllib`. If you find yourself wanting to import something in the domain that touches the outside world, add a Protocol or callable to the domain and let the application layer inject the implementation. The full rule is in [docs/docs/domain/invariants/domain.md](docs/docs/domain/invariants/domain.md).

## Adding a rule

Open `src/tidyra/resources/default_rules.toml` and append a new `[[rule]]` table. To override a built-in rule for yourself, copy the file to your user config dir and edit it there — see [docs/docs/tooling/configuration.md](docs/docs/tooling/configuration.md) for the path on each OS.

## Adding a strategy

A strategy turns `(root, entries, rules)` into an `OrganizationPlan`. Create a new module under `src/tidyra/domain/strategies/`, implement the `OrganizationStrategy` Protocol, and wire it into `OrganizeService` (or add a separate service if it's optional). Strategies must be pure: no filesystem I/O, no Flet, no logging side effects. See [ADR-0002](docs/docs/adrs/0002-strategy-protocol-for-llm-swap.md) for the rationale.

## Adding a view

1. Create `src/tidyra/presentation/views/<name>.py` with a `def <name>_view(app: TidyraApp) -> ft.Control:` function.
2. Add a `Screen` enum entry in `state.py` if the view is a new screen.
3. Wire the screen into `TidyraApp.render`.
4. Use `if TYPE_CHECKING:` for the `TidyraApp` import to avoid the circular dependency between views and the controller.

Views must be thin: hand off to the controller, render the returned data, no logic. The full rule is in [docs/docs/frontend/invariants/frontend.md](docs/docs/frontend/invariants/frontend.md).

## Adding a component

Components are reusable Flet controls under `src/tidyra/presentation/components/`. Each is a function that returns an `ft.Control`. They take callbacks for events rather than importing the controller, to keep them easy to test.

## Submitting changes

1. Fork the repo and create a branch (`git checkout -b my-change`).
2. Make your change. Run `uv run ruff check .` and `uv run mypy src` before committing.
3. If the change introduces or modifies a decision that shapes the codebase, add or update an ADR under `docs/docs/adrs/`. If the change is a non-trivial bug fix, add a section to the day's fix log under `docs/docs/known-issues/`.
4. Commit with a clear subject. The format is in [docs/docs/processes/invariants/processes.md §3](docs/docs/processes/invariants/processes.md#3-commit-messages--agent-writes-user-commits). The agent writes the message; you run the commit. Never add the AI/agent's name as co-author.
5. Open a pull request describing the change, the motivation, and any screenshots for UI work.

## Release notes

Tidyra follows [Keep a Changelog](https://keepachangelog.com/) format in [`CHANGELOG.md`](CHANGELOG.md). The release flow is in [docs/docs/processes/invariants/processes.md §5](docs/docs/processes/invariants/processes.md#5-release-flow).

## Code of conduct

Be respectful. We're all here to make a small, useful piece of software.