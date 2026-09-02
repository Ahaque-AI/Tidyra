# Tidyra

![Tidyra logo](src/tidyra/resources/tidyra-logo.svg)

> A safe, deterministic, rule-based folder organizer with a Flet desktop UI.

Tidyra scans a folder you choose (typically `~/Downloads`), classifies each
file with configurable rules, shows you a preview of the proposed
organization, and only moves files after you confirm. Nothing is deleted,
nothing is overwritten silently, and the preview is a real
`OrganizationPlan` — the same plan is what the executor runs.

## Features

- **Rule-based classification.** Ships with sensible defaults for Images,
  Documents, Music, Videos, Archives, Applications, Code, and a `Misc/`
  catch-all. Override or extend them via TOML.
- **Three-step workflow.** Pick a folder → preview the plan → confirm to
  organize. Nothing happens until you press the button.
- **Safety first.** No deletion, no silent overwrite, no symlink following,
  no moves outside the chosen root, no recursive re-organization in a
  single run.
- **Strategy abstraction.** The rule-based engine is one
  implementation of an `OrganizationStrategy` Protocol. A future LLM
  strategy can produce the same `OrganizationPlan` without touching the
  filesystem.
- **Cross-platform desktop.** Single Python codebase; runs on Windows,
  macOS, and Linux via Flet.
- **Structured logging.** Every scan, move, skip, and rule-match is
  recorded via [loguru](https://loguru.readthedocs.io/) with bound
  context (`root`, `file_path`, `rule_name`, …). Mirror to a
  JSON-lines file with `TIDYRA_LOG_FILE` for downstream tooling.
- **Pure-domain core.** The domain layer has zero Flet, zero TOML, and
  zero filesystem imports — it's testable without launching a UI.

## Screenshots

> Placeholder. Once the UI stabilizes, drop a screenshot here.

## Quick start

Install [uv](https://docs.astral.sh/uv/) if you don't have it, then:

```powershell
git clone https://github.com/abdulhaque/tidyra.git
cd tidyra
uv sync
uv run tidyra
```

The first `uv sync` installs Python, Flet, and platformdirs. `uv run tidyra`
opens the desktop window.

## Usage

1. Pick a folder. Click *Select Folder* in the home view.
2. Scan. Click *Scan*. Tidyra shows every file it found and how the
   rules classified it.
3. Preview. The preview view lists every move it plans to make and
   every file it will skip, with reasons.
4. Organize. Click *Organize Files*. The preview becomes the result
   screen; failures (if any) are listed separately.

## Configuration

Tidyra looks for rules in this order; the first that exists wins:

1. User config dir — `rules.toml`
   - Windows: `%APPDATA%\tidyra\rules.toml`
   - macOS: `~/Library/Application Support/tidyra/rules.toml`
   - Linux: `~/.config/tidyra/rules.toml`
2. `rules.toml` in the current working directory.
3. Built-in defaults shipped with the app.

Example override (`rules.toml` in the user config dir):

```toml
[[rule]]
name = "raw-photos"
destination = "Photos/RAW"
extensions = [".cr2", ".nef", ".arw", ".dng"]
priority = 20  # higher than the built-in 'images' rule

[[rule]]
name = "papers"
destination = "Papers"
extensions = [".pdf"]
priority = 15
```

See [docs/docs/tooling/configuration.md](docs/docs/tooling/configuration.md) for the full schema,
precedence rules, and conflict semantics.

## Architecture

```
Flet Presentation
        ↓
Application Services
        ↓
Domain
        ↑
Infrastructure
```

The domain layer is pure: no Flet, no `tomllib`, no real `pathlib` I/O.
Strategies are pluggable — a future `LLMStrategy` will satisfy the same
`OrganizationStrategy` Protocol and produce the same `OrganizationPlan`.
See [docs/docs/domain/architecture.md](docs/docs/domain/architecture.md) and the
[rationale in ADR-0001](docs/docs/adrs/0001-four-layer-architecture.md).

## Documentation

The full docs site lives under [docs/docs/](docs/docs/index.md).
Start at [docs/docs/index.md](docs/docs/index.md) (the knowledge domain map) and
follow the routing. The rules that apply to every task are in
[docs/docs/core/invariants/core.md](docs/docs/core/invariants/core.md).

## Development

```powershell
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run python -m tidyra        # smoke launch
```

Add a dependency: `uv add <package>`. Add a dev tool: `uv add --dev <package>`.

See [docs/docs/tooling/development.md](docs/docs/tooling/development.md) for how to add a rule, a
strategy, or a view.

## Roadmap

The current release is **alpha** — Phase 1 from the roadmap. Future
phases add undo, custom rule editor, an optional LLM strategy, and
scheduled organization. See [docs/docs/processes/roadmap.md](docs/docs/processes/roadmap.md).

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for setup,
the docs-routing workflow, and how architectural decisions are captured
as ADRs.

## License

[MIT](LICENSE).