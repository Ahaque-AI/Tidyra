# Tidyra

![Tidyra logo](src/tidyra/resources/tidyra-logo.svg)

> A safe, deterministic, rule-based folder organizer with a Flet desktop UI.

Tidyra scans a folder you choose (typically `~/Downloads`), classifies each
file with configurable rules, shows you a preview of the proposed
organization, and only moves files after you confirm. Nothing is deleted,
nothing is overwritten silently, and the preview is a real
`OrganizationPlan` — the same plan is what the executor runs.

## Features

- **Rule-based classification — names and formats together.** Ships
  with sensible defaults for vacation photos, screenshots, RAW
  photos, invoices, tax documents, music, videos, archives, code,
  and a `Misc/` catch-all. Rules can match on extension, file name
  glob, or both. Override or extend via TOML.
- **Nested destinations with `{year}` / `{month}` templates.**
  `Documents/Finance/Tax/{year}` creates per-year buckets
  automatically as new files arrive. `Photos/{year}` organises photos
  by their mtime year.
- **Three-step workflow.** Pick a folder → preview the plan → confirm
  to organize. Nothing happens until you press the button.
- **Optional recursive scan.** Walk every file under the chosen root
  and preserve the original folder layout inside each rule's
  destination. Toggle in the home view; default is on.
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

### From a binary release (recommended for most users)

Download the build that matches your OS from
[Releases](https://github.com/abdulhaque/tidyra/releases):

| OS | File | Notes |
|---|---|---|
| Windows | `tidyra-windows-x64.zip` | Unzip and run `tidyra.exe`. |
| macOS (Apple Silicon) | `tidyra-macos-arm64.zip` | Unzip and run the `.app`. First launch may require `xattr -d com.apple.quarantine` because the build is unsigned. |
| Linux | `tidyra-x86_64.AppImage` | `chmod +x tidyra-x86_64.AppImage && ./tidyra-x86_64.AppImage`. |

The release artifacts are produced by GitHub Actions on every `v*.*.*`
tag push — see [docs/docs/tooling/invariants/tooling.md §10](docs/docs/tooling/invariants/tooling.md#10-cross-platform-packaging--flet-build--github-actions) and [ADR-0009](docs/docs/adrs/0009-cross-platform-packaging.md).

### From source

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

### Building a release locally

```powershell
uv run python tools/build_icon.py                # regenerate icons from the SVG
uv run flet build windows `
  --project tidyra --product Tidyra `
  --org dev.abdulhaque --bundle-id dev.abdulhaque.tidyra `
  --copyright "MIT License"
```

The first build downloads the Flutter SDK; subsequent builds reuse the
cache. macOS and Linux builds work the same way with `flet build macos`
and `flet build linux`. The entry point is configured in
`pyproject.toml`'s `[tool.flet.app]` block (`path = "src/tidyra"`,
`module = "main"`); the build finds `src/tidyra/main.py` (an entry
shim that re-exports the real `tidyra.presentation.app.main`). See
[tooling/invariants/tooling.md §10](docs/docs/tooling/invariants/tooling.md#10-cross-platform-packaging--flet-build--github-actions)
for the full set of flags.

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