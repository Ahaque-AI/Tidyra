# ADR-0011: Explicit empty-directory cleanup

- Status: Accepted
- Date: 2026-09-03
- Deciders: Abdul Haque, Mavis
- Context: Previous organization layouts leave empty category folders behind. Users need Tidyra to clear those folders without risking files or non-empty directories.

## Decision

Provide an unchecked cleanup option before scanning. When selected, the plan lists every directory that will be checked after moves and the final action names empty-folder removal. The executor may call only `Path.rmdir()` through `LocalFileSystem.remove_empty_directory()`, which rejects symlinks and Windows junctions and succeeds only when the directory is empty at that moment.

## Consequences

- Positive: old empty output folders can be cleared from the selected root without manual cleanup.
- Positive: files, non-empty directories, symlinks, and junctions remain untouched.
- Negative: a directory listed in preview may remain when it is not empty at execution time.
- Follow-ups: do not add recursive deletion or automatic cleanup without a new ADR and explicit user confirmation design.
