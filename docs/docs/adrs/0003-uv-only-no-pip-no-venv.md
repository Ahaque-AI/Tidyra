# ADR-0003: uv as the only package manager

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra has a single Python codebase, a single lockfile, and one CI pipeline. Adding multiple package managers creates divergent environments and silent drift between local and CI.

## Decision

`uv` is the only sanctioned tool for:

- Running Python (`uv run tidyra`, `uv run python ...`).
- Managing dependencies (`uv add`, `uv add --dev`, `uv lock`, `uv sync`).
- The lockfile (`uv.lock`) is committed and the only allowed one.

`pip`, `requirements.txt`, `pip-tools`, `pipenv`, `poetry`, `conda`, manual `python -m venv`, and any parallel packaging workflow are forbidden. The rule is enforced by code review and the onboarding docs.

## Consequences

- Positive: one toolchain, one lockfile. Onboarding is `git clone && uv sync`.
- Positive: CI uses the same toolchain — no "works on my machine" drift.
- Negative: contributors unfamiliar with `uv` have a small learning step. The README and CONTRIBUTING cover it.
- Negative: any tooling that expects `requirements.txt` (rare for a desktop app) cannot be added without an ADR.
- Follow-ups: keep the README and CONTRIBUTING in lockstep with this rule; update both if `uv` ever drops the commands we rely on.