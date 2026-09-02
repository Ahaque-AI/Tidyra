# Known issues / fix log

Bug-fix writeups and incident notes. Append-only, ordered by date. AGENTS.md stays under 100 lines — fix logs are where the receipts live.

## Index

| Date | File | Summary |
|---|---|---|
| 2026-09-02 | [fix-log-2026-09-02.md](fix-log-2026-09-02.md) | `FilePicker` service registration; nested-scroll removal on Preview/Results |

## Authoring rule

When something non-trivial is fixed:

1. Add a new section to `fix-log-YYYY-MM-DD.md` (create the file if it does not exist).
2. Record the symptom, the root cause, the change, and any regression risk.
3. Add a row to this index.
4. Link the fix log entry from any rule doc that codifies the lesson (e.g. the Flet 0.86+ service-registration rule in `frontend/invariants/frontend.md`).

See [processes/invariants/processes.md §2](../processes/invariants/processes.md#2-bug-fixes--fix-log) for the meta-rule.