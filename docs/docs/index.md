# Tidyra — Knowledge Map

Tidyra is a small, safe, deterministic folder organizer. Its codebase is split into a handful of knowledge domains, each owning one concern. Pick the domain that matches your task before reading anything else.

## Domains

| Domain | Concern | When to load |
|---|---|---|
| [core](core/index.md) | Working rules that apply to every task — read AGENTS.md, follow the routing, do not explore blindly. | Always. Start here. |
| [domain](domain/index.md) | Pure-Python rules for the domain layer (no Flet, no I/O, no TOML). | Editing `src/tidyra/domain/*` or adding a strategy. |
| [frontend](frontend/index.md) | Flet UI rules — presentation layer stays thin, components are reusable, brand lives here. | Editing `src/tidyra/presentation/*` or touching the window/window icon/UI text. |
| [security](security/index.md) | Filesystem safety, secrets, no destructive remote actions without confirmation. | Anything that touches the filesystem, paths, env vars, or remote services. |
| [tooling](tooling/index.md) | uv, ruff, mypy, pyproject, packaging, build. | Adding deps, changing build, lint/type CI, file paths on Windows. |
| [processes](processes/index.md) | Plans, ADRs, cadence, README, CONTRIBUTING, releases, fix logs. | Writing a plan, capturing an architectural decision, updating public docs, releasing. |

## Adjacent landing pages

These are not rules — they're how-to / what-is pages that complement the domain entries above.

- [README.md](../../README.md) — public GitHub-facing landing page.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — contributor onboarding and the workflow that ties this docs site together.
- [CHANGELOG.md](../../CHANGELOG.md) — release notes.
- [LICENSE](../../LICENSE) — MIT.

## Cross-cutting repositories

- [ADRs](adrs/index.md) — every architectural decision that shapes the codebase, numbered and dated. Read before changing a layer boundary, swapping a dependency, or replacing a pattern.
- [Known issues / fix log](known-issues/index.md) — bug-fix writeups, ordered by date. Append-only.