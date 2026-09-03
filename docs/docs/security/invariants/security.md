# Security rules

## 1. Filesystem safety lives in `PlanValidator`

The seven guarantees in [architecture.md](../../../architecture.md) (no delete, source must be a regular file, destination must resolve inside `root`, no symlink following, no silent overwrite, drop no-op moves, no nested destinations) are enforced exactly once, in `PlanValidator`. Do not duplicate the checks anywhere else — the executor consumes a plan that already says "execute" or "skip" with a `SkipReason`.

## 2. The preview is the plan

The preview UI and the executor both consume the **same** `OrganizationPlan`. There is no "we'll re-derive what to move at execute time" path. If you find yourself wanting to compute a second plan at execution, fix the architecture; do not duplicate the logic.

## 3. Symlinks are recorded but never followed

`FileEntry.is_symlink` is metadata, not a hint. `LocalFileSystem.scan` records the flag and `PlanValidator` rejects the operation with `SkipReason.SYMLINK`. Do not "support symlink following" — the protection is deliberate. If a user really wants to move a symlink, they can replace it with the target first.

## 4. Remove only explicitly selected empty directories

Tidyra never deletes files and never recursively deletes a directory. Empty-directory removal is available only when the user selects it before scanning; the preview lists every directory that will be checked and the final action names the removal. `LocalFileSystem.remove_empty_directory()` rejects symlinks and Windows junctions, then uses non-recursive `Path.rmdir()` as the final atomic emptiness check. A directory that contains anything at removal time remains untouched. See [ADR-0011](../../adrs/0011-explicit-empty-directory-cleanup.md).

## 5. No destructive remote action without confirmation

Anything that pushes, drops, or destroys a remote resource (a Denodo datasource, a S3 bucket, a database, a remote container) MUST have explicit user confirmation in the current session. The UI/CLI must ask — confirm dialog or `--yes` guard — before the drop call is sent. Never drop a remote resource silently, programmatically, or as part of an unconfirmed batch. The session-long allowance for "user already said yes" does not exist; each destructive action requires a fresh confirmation.

## 6. Env-var values stay out of comments

No example values for env vars in code comments. `e.g. admin` next to `DENODO_PASSWORD` is a security smell — never add it to comments, docstrings, config examples, or README code blocks. Allowed in code: actual function calls, error messages that name the variable only, generic descriptions. Not allowed: example values, "set X to Y" patterns.

The same rule applies to commit messages — no env var names, no values, no examples. Refer to features abstractly ("secrets wired", "image pins updated") not by specific env var names.

## 7. No hardcoded credentials — anywhere tracked

Credentials live in `.env` / `.env.local`, read via Pydantic `Settings` or `os.environ` is not used directly in code. No `user:pass@host` strings in any tracked file — `.env.example` documents the *names* and shapes, not values. `docker-compose`, Alembic `env.py`, scripts, READMEs — none of them embed secrets.

## 8. Logging never leaks credentials

Use `loguru` with bound context, never `print`. Sensitive fields (`Authorization`, `Cookie`, `password`, `token`, …) MUST be redacted in any structured sink that mirrors records to disk (`TIDYRA_LOG_FILE`). Failures log with `logger.exception(...)` so the traceback points at the real failing line; do not log the failing value.

## 9. Confirm a destructive read

Operations that *appear* read-only but are destructive (deleting a lock file, truncating a log, deleting empty parent directories after a move) require the same confirmation as a write. If in doubt, treat it as destructive.
