# Tooling

uv, ruff, mypy, pyproject, packaging. Anything that makes the build, lint, type-check, or release work lives here.

Start with [invariants/tooling.md](invariants/tooling.md). It is short and absolute.

- [Invariants](invariants/index.md)
- [tooling.md](invariants/tooling.md)
- [Configuration](../../configuration.md) — TOML rule format and discovery order.

## What the tooling layer owns

| Concern | Where |
|---|---|
| Package manager | `uv` (mandatory; no `pip`, no `requirements.txt`, no manual `venv`) |
| Python interpreter | Bundled with `uv`, declared `>=3.11` in `pyproject.toml` |
| Lint + format | `ruff check .` and `ruff format .` |
| Type check | `mypy src` (strict) |
| Build backend | `hatchling` (see `pyproject.toml [build-system]`) |
| Resource packaging | `src/tidyra/resources/*.toml` + `*.svg` via hatch artifacts |

## Adding dependencies

```powershell
uv add <package>
uv add --dev <package>
```

Both commands update `pyproject.toml` and `uv.lock`. Never edit `uv.lock` by hand. Never commit a `pyproject.toml` change without its matching lockfile change.

## Daily commands

See [development.md](../../development.md) for the full table. The recurring ones:

```powershell
uv sync --extra dev
uv run ruff check .
uv run ruff format .
uv run ruff format --check .
uv run mypy src
uv run tidyra
```