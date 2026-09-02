# Changelog

All notable changes to Tidyra are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Brand mark: `src/tidyra/resources/tidyra-logo.svg` — folder with three
  tidied file cards in deep teal (`#0F766E`) and light teal (`#5EEAD4`).
  Wired into the desktop window via `page.window.icon` and the home
  view header via `tidyra.presentation.brand.logo_path()`. See
  [ADR-0007](docs/docs/adrs/0007-tidyra-brand-mark.md).
- `tidyra.presentation.brand` — single source of truth for loading the
  brand asset via `importlib.resources`. Captured as
  [ADR-0006](docs/docs/adrs/0006-importlib-resources-for-packaged-assets.md).
- AGENTS.md — single routing + meta-rules file at the repo root
  (`<100 lines`). The full docs site lives under `docs/docs/`.
- Docs site at `docs/docs/` with six knowledge domains
  (`core`, `domain`, `frontend`, `security`, `tooling`, `processes`),
  each with its own `index.md` and `invariants/`.
- ADRs at `docs/docs/adrs/` — seven seed ADRs capturing every
  architectural decision that shaped the initial scaffold.
- Known-issues / fix log at `docs/docs/known-issues/`.

### Changed
- README, CONTRIBUTING, and CHANGELOG point at the new docs locations
  and explain the AGENTS.md routing.
- `pyproject.toml` packages `*.svg` resources alongside `*.toml`.

### Removed
- Top-level `docs/architecture.md`, `docs/configuration.md`,
  `docs/development.md`, and `docs/roadmap.md` — relocated under
  `docs/docs/<domain>/` to match the new docs site layout.

## [0.1.0] - 2026-09-02

### Added
- First public release of the initial scaffold.

[Unreleased]: https://github.com/abdulhaque/tidyra/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/abdulhaque/tidyra/releases/tag/v0.1.0