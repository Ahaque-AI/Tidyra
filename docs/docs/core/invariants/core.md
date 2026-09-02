# Core rules — every task

These rules apply to anything you do in this repo, in any layer. Domain-specific docs inherit from here.

## 1. Read before you write

Open [docs/docs/index.md](../../index.md) first. Pick the domain that matches your task and follow the routing path down to the relevant rule doc. Do not load every rule doc — only the one your task needs.

## 2. The routing path is the spec

```
docs/docs/index.md
  → <domain>/index.md
    → <domain>/invariants/index.md
      → <domain>/invariants/<rule>.md
        → source code
          → implementation
```

Stop reading at the layer that answers your question. Going deeper when the rule doc already covers it wastes context and dilutes the answer.

## 3. Never go exploring

Do not crawl the source tree when a doc already covers the question. The only reasons to open a source file are:

1. The docs do not answer.
2. The user explicitly asks for implementation details.
3. The task is to implement and the rule doc says "do X" — verify X exists or behaves as described before editing.

## 4. AGENTS.md is the only meta-doc

AGENTS.md is the routing + meta-rules file. It is the only place the agent reads "before everything else". Keep it under 100 lines. If a meta-rule does not fit in AGENTS.md, push it into a `processes` invariant instead.

## 5. Do not create INSTRUCTIONS.md

There is no separate INSTRUCTIONS.md, CLAUDE.md, or any other "agent instructions" file. All working rules live under `docs/docs/`. New rules belong in the right invariant doc, not in a parallel file.

## 6. AGENTS.md does not capture fixes

Bug fixes, incident reports, and "we learned X" writeups do not belong in AGENTS.md. They live in `docs/docs/known-issues/fix-log-YYYY-MM-DD.md` and are linked from `docs/docs/known-issues/index.md`. AGENTS.md is for stable, recurring rules only.

## 7. Confirm before destroying

Any action that pushes, deletes a remote resource, rebuilds a container, drops a Denodo datasource, or removes a tracked file MUST have explicit user confirmation in the current session. "User asked earlier in the day" is not confirmation.

## 8. Commits belong to the user

The agent writes the commit message and stages the change. The user runs `git commit`. Never run `git commit` from the agent. Never add the AI/agent's name as co-author. See [processes/invariants/processes.md](../../processes/invariants/processes.md) for the format.

## 9. One concern at a time

If a task expands into two unrelated concerns, finish and hand off the first before starting the second. Do not silently bundle unrelated edits into the same commit.

## 10. Skills live with the routing

Default-active skills:

- **Ponytail** — simplest solution, shortest working diff.
- **impeccable** — load before any frontend UX review / polish / audit.
- **ui-ux-pro-max** — load only before a visual redesign / overhaul.
- **backend-security-coder** — load proactively before any backend security implementation or security code review.

Do not load a skill that does not match the task.