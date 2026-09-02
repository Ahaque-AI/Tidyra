# Security

Tidyra moves real files on the user's machine. Every path operation, every cross-folder move, and every "we should add an env var" decision lands here.

Start with [invariants/security.md](invariants/security.md). It is short and absolute.

- [Invariants](invariants/index.md)
- [security.md](invariants/security.md)
- [Architecture](../architecture.md) — the safety guarantees enforced by `PlanValidator`.

## What the security layer owns

- The seven guarantees in [architecture.md](../architecture.md#safety-guarantees) (no delete, source must be a regular file, destination must resolve inside `root`, no symlink following, no silent overwrite, drop no-op moves, no nested destinations).
- Credential / env-var hygiene — see [env-var rule](../security/invariants/security.md#6-env-var-values-stay-out-of-comments).
- Confirmation prompts before any destructive remote action.

The application never sees raw `pathlib` for mutations: it goes through `FileSystem`, which `infrastructure` implements and `PlanValidator` gates. The layer boundary itself is the first line of defence.