# Tooling rules

## 1. `uv` only — no `pip`, no `requirements.txt`, no manual `venv`

Tidyra's Python interpreter, virtualenv, dependency manager, and script runner are all `uv`. Reasons:

- One tool, one lockfile (`uv.lock`).
- The CI uses the same toolchain.
- Onboarding is `git clone && uv sync` — no "now install Python".

Never add `requirements.txt`, never document `pip install -r ...`, never run `python -m venv`. If you need a new dependency, `uv add <package>`.

## 2. `pyproject.toml` is the project config

- `[project]` — name, version, dependencies, optional-dependencies, scripts, urls.
- `[build-system]` — `hatchling` only; do not change the build backend without an ADR.
- `[tool.ruff]` + `[tool.ruff.lint]` + `[tool.ruff.format]` — lint and format rules.
- `[tool.mypy]` — strict mode.

If you add a runtime dep, also update `[project.optional-dependencies]` if it is dev-only.

## 3. mypy is strict

`pyproject.toml` declares `strict = true` plus `warn_unused_ignores`, `warn_return_any`, `disallow_untyped_defs`. Domain code (`src/tidyra/domain/`) MUST stay 100% type-clean. Adding a `# type: ignore` requires an inline comment explaining why — and ideally a follow-up issue.

## 4. ruff lint and format must pass

`uv run ruff check .` and `uv run ruff format --check .` are the CI gate. New code should follow the existing rules — do not silence a lint with a `# noqa` unless you can justify it in the PR description.

## 5. Resource packaging

Anything in `src/tidyra/resources/` that needs to ship with the wheel must be listed under `[tool.hatch.build.targets.wheel].artifacts`. Today:

```toml
artifacts = ["src/tidyra/resources/*.toml", "src/tidyra/resources/*.svg"]
```

If you add a new resource type (e.g. `.json`, `.css`), extend the glob — or, if the asset is large, switch to `[tool.hatch.build.targets.wheel.force-include]`.

## 6. Load packaged resources via `importlib.resources`

Do not hard-code paths under `src/tidyra/resources/...` from code. Use `from importlib.resources import files; files("tidyra.resources").joinpath("name.ext")`. The pattern is documented in [presentation/brand.py](../../../frontend/brand.py).

## 7. Windows path discipline

- Use `pathlib.Path` — never `os.path.join`.
- Do not assume forward slashes. `Path("a/b")` is portable.
- Flet desktop APIs that expect paths accept `Path` or `str`; pass `str(Path(...))` if the API chokes on `Path`.
- Test the Windows shell with PowerShell syntax; do not embed `bash` snippets in user-facing docs. The README and CONTRIBUTING use PowerShell examples.

## 8. No global Python

Do not call `python` directly for project commands. `uv run python ...` is the only sanctioned way to invoke a one-off Python snippet during development. CI runs `uv run python ...` too.

## 9. Lockfile commits travel with dep changes

`uv.lock` is committed. Every change to `pyproject.toml` dependencies must include the matching `uv.lock` change in the same commit. A dep-only change without a lockfile change is a CI red flag.