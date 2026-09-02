# AGENTS.md

Single source of truth for working rules. No separate INSTRUCTIONS.md.

## Routing

```
AGENTS.md (this file — routing + meta rules)
    ↓
docs/docs/index.md (knowledge domain map)
    ↓
relevant domain/index.md
    ↓
relevant invariants/index.md
    ↓
specific rule doc (core.md, domain.md, frontend.md, security.md, tooling.md, processes.md)
    ↓
source code (ground truth)
    ↓
implementation
```

## Rules

All rules live in `docs/docs/<domain>/invariants/`. Pick the rule doc that matches your current task — never load all of them.

| Task | Rule doc |
|---|---|
| Any task | `docs/docs/core/invariants/core.md` |
| Python domain layer | `docs/docs/domain/invariants/domain.md` |
| Flet / presentation | `docs/docs/frontend/invariants/frontend.md` |
| Filesystem safety, secrets | `docs/docs/security/invariants/security.md` |
| uv, ruff, mypy, pyproject | `docs/docs/tooling/invariants/tooling.md` |
| Plans, ADRs, cadence, README | `docs/docs/processes/invariants/processes.md` |

## Never go exploring

For anything related to this repo, check the docs first. Only go into source when: (1) the docs don't answer, (2) the user explicitly asks for implementation details, or (3) the task is to implement and docs say to do X — verify X in the source first.

## Architectural decisions (ADRs)

When a decision shapes the codebase — new dependency, framework choice, layer boundary, replacement of an existing pattern — capture it. See `docs/docs/processes/invariants/processes.md` for the workflow. Quick version:

1. Add `docs/docs/adrs/NNNN-<kebab-title>.md` using the MADR template.
2. Add a row to `docs/docs/adrs/index.md`.
3. If the decision changes a public doc (README, configuration, etc.), update that doc in the same change.
4. Link the ADR from any rule doc it touches.

## Session-level rules

- Capture fixes in their own docs file. When something non-trivial is fixed, drop a section in `docs/docs/known-issues/fix-log-YYYY-MM-DD.md` and link it from `docs/docs/known-issues/index.md`.
- AGENTS.md is for working rules. Bug-fix writeups belong with the other incident reports.
- This file stays under 100 lines.

## Destructive actions

Always confirm before pushing, deleting, or rebuilding containers.

## Commits

Never run `git commit` without explicit user confirmation in the current session. Stage the change, propose the commit message (see `docs/docs/processes/invariants/processes.md`), and let the user commit. The agent writes the message — the user owns the commit. Same class of action as pushing, deleting, or rebuilding containers.

Never add the AI/agent's name as co-author. Commits belong to the user.

## Skills

- Frontend UX review / polish / audit → `impeccable` skill.
- Visual redesign / overhaul → `ui-ux-pro-max` skill.
- Backend security implementation → `backend-security-coder` skill.
- Simplest solution, shortest working diff → `Ponytail` skill (active by default).