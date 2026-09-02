# Roadmap

Tidyra is being built in four phases. This document lists what's in
each phase. Items are aspirational until they ship; the implementation
status of each phase lives in [`CHANGELOG.md`](../../../CHANGELOG.md).

## Phase 1 — Rule-based foundation (current)

Shipped:

- Domain layer (`FileEntry`, `OrganizationRule`, `OrganizationPlan`,
  `SkipReason`, `PlanValidator`, `OrganizationResult`).
- Strategy abstraction (`OrganizationStrategy` Protocol,
  `RuleBasedStrategy` implementation).
- Filesystem abstraction (`FileSystem` Protocol, `LocalFileSystem`).
- Configuration via TOML with built-in defaults.
- Flet desktop UI (home / preview / results views).
- Safety guarantees: no deletion, no silent overwrite, no symlink
  following, no moves outside the chosen root.

## Phase 2 — UX polish

Goal: make the existing workflow more forgiving and more powerful.

- **Undo / history.** Every successful run is recorded. Restore moves
  via an Undo button on the results screen.
- **Better conflict resolution UI.** When the preview shows a
  `DESTINATION_EXISTS` skip, let the user pick: skip, rename, overwrite
  (the last only with an explicit confirmation).
- **Custom rule editor.** Edit rules in the UI without leaving the app.
  Saves back to the user config TOML.
- **Multi-folder selection.** Organize several folders in one run.
- **Filter and search.** Type-ahead filter for the preview list when
  there are many files.

## Phase 3 — LLM strategy

Goal: let the user describe intent in natural language; the LLM returns
an `OrganizationPlan`.

- New `LLMStrategy` satisfying `OrganizationStrategy`.
- Strategy reads natural-language context from the user (e.g.
  "Put everything from the Smith wedding into a `Wedding/` folder and
  split RAW photos into `Photos/RAW`").
- The LLM **never** touches the filesystem. It returns a plan; the same
  validator and executor apply it.
- Optional local model support; default cloud provider configurable
  via env vars.

The strategy abstraction exists today; Phase 3 is implementation, not
architectural change.

## Phase 4 — Scheduling and integrations

Goal: make Tidyra something you can leave running.

- **Scheduled scans.** Run an organize pass on a folder on a schedule
  (cron-style) or in response to filesystem events.
- **Background mode.** Keep Tidyra running in the system tray and apply
  rules as new files arrive.
- **Trash / archive integration.** On macOS, move deleted files to the
  Trash; on Linux, integrate with `trash-cli`; on Windows, use the
  Recycle Bin.
- **Notifier hooks.** Optional Slack / email / webhook on run
  completion.

## Things that will not happen

These were considered and explicitly cut:

- A web frontend. Tidyra is a desktop app.
- A database. Tidyra reads configuration from TOML and the filesystem
  at scan time.
- Telemetry or analytics. There are no network calls in the codebase.
- An auth layer. Tidyra is a single-user local app.
- A cloud-hosted version. The app runs against the user's own files.

If a future feature request would require one of these, it's a signal
to rethink, not to add infrastructure.
