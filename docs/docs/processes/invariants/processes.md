# Process rules

## 1. Architectural decisions → ADR

When a decision shapes the codebase — a new dependency, a framework choice, a layer boundary, a replacement for an existing pattern, a name change that ripples through the public API — write an ADR. Format and workflow below.

### File location and naming

```
docs/docs/adrs/NNNN-<kebab-title>.md
```

`NNNN` is the next available four-digit zero-padded number. Title is `kebab-case`, short, descriptive.

### Template (MADR-mini)

```markdown
# ADR-NNNN: <Title>

- Status: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
- Date: YYYY-MM-DD
- Deciders: Abdul Haque, Mavis
- Context: <what triggered the decision>

## Decision

<what we are doing, in one or two sentences>

## Consequences

- Positive: <upside>
- Negative: <downside>
- Follow-ups: <what else must change because of this>
```

### Workflow

1. Add `docs/docs/adrs/NNNN-<title>.md`.
2. Add a row to `docs/docs/adrs/index.md`.
3. If the decision changes a public doc (README, configuration.md, etc.), update that doc in the same change.
4. Link the ADR from any rule doc it touches (e.g. if it changes a domain-layer invariant, link from `docs/docs/domain/invariants/domain.md`).
5. The agent captures the ADR when it spots an architectural decision; the user confirms the wording.

## 2. Bug fixes → fix log

When something non-trivial is fixed, drop a section in `docs/docs/known-issues/fix-log-YYYY-MM-DD.md` and link it from `docs/docs/known-issues/index.md`. Each fix log entry records: the symptom, the root cause, the change, the regression risk. AGENTS.md stays under 100 lines — fix logs are where the receipts live.

## 3. Commit messages — agent writes, user commits

The agent proposes a commit message. The user runs `git commit`. See [core rules](../../core/invariants/core.md) §8 for the meta-rule; this section covers the format.

### Format

```
<type>(<scope>): <short subject>

- <concrete change> (<file/folder>)
- <concrete change> (<file/folder>)
- ... (3–8 bullet lines)
```

### Subject line

- One line, type + scope, concise.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`.
- Scopes: a layer or area name (`tidyra`, `presentation`, `domain`, `config`, `ci`, `docs`).
- Under 72 characters. Self-explanatory without the body.

### Body bullets

- 3–8 lines. Each line says WHAT and WHERE (file or folder).
- Plain words, no jargon.
- Cover ONLY the diff. Never re-list earlier steps.
- One commit per batch. When 2–3+ steps land together, give one consolidated message.

### Forbidden

- AI/agent name as co-author or contributor. Commits belong to the user.
- Env-var names, values, or examples. Refer to features abstractly.
- "AI-generated" footers, "Co-authored-by: <model>", or any other agent-self-promotion.

## 4. README maintenance

README.md is automatic, not opt-in. When relevant work lands (new feature, new rule, new dep, new public surface), update README in the same change. The README must match reality — keep the install commands, the feature list, the screenshot placeholders, and the doc links in sync.

After updating the README, mention it in the handoff so the user knows it changed and why.

## 5. Release flow

1. Bump version in `pyproject.toml`.
2. Move `[Unreleased]` items in `CHANGELOG.md` to a dated section (`## [X.Y.Z] - YYYY-MM-DD`).
3. Update the link targets at the bottom of `CHANGELOG.md` (`[Unreleased]`, `[X.Y.Z]`).
4. Tag and push. CI builds and publishes when CI exists.
5. Open a release on GitHub summarising the change in user-facing language (no internal jargon, no `feat():` subject line — the release is for users, not the changelog).

## 6. One concern per commit

If a change bundles two unrelated fixes or features, split them. A bug fix to the file list and a new view are two commits, not one. The exception is the initial scaffold (one commit is fine because there is nothing earlier to break).

## 7. Plans live under `docs/plans/`

When you plan a feature that is too big to fit in a single conversation, drop a `docs/plans/<date>-<feature>.md` doc. The plan must list the steps in order, declare dependencies between steps, and identify what verifies each step. The plan is read by both the user and the agent before any code lands.