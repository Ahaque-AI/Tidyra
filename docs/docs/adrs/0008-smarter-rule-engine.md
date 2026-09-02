# ADR-0008: Smarter rule engine — name patterns, nested destinations, recursive scan

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra's first rule engine only matched on file extensions and produced flat destinations, one level deep, by scanning only the direct children of the chosen root. The user wanted smarter classification by name, nested destination folders, and the ability to walk subdirectories.

## Decision

Three changes to the rule engine, replacing the v0.1.0 one-matcher model:

1. **Name-and-extension matching.** `OrganizationRule` gains `name_patterns: tuple[str, ...]` (case-insensitive globs). When both `extensions` and `name_patterns` are set on a rule, the file must satisfy **both** — the "name AND format together" semantic. When only one is set, that single condition decides. The legacy `always_matches: bool` is retained for v0.1.0-config backward compatibility but new rules should use `name_patterns = ["*"]`.
2. **Destination templates.** `destination` may contain `{year}`, `{month}`, `{ext}`, `{stem}`. `render_destination(template, entry)` expands them from `FileEntry` fields. `{year}` and `{month}` use `entry.mtime`; we never read file contents. Unknown placeholders stay as literal text.
3. **Recursive scan.** `FileSystem.scan(root, *, recurse: bool = False)`. When `recurse=True`, every regular file under `root` is returned, preserving the relative path; the destination is computed as `root / <rule destination> / <relative-under-root>` so `Downloads/2024/photo.jpg` with rule destination `Photos/{year}` lands at `Photos/2024/photo.jpg`. The UI exposes the toggle (default on). `PlanValidator` still rejects nested destinations and moves outside the root.

## Consequences

- Positive: smarter classification matches real-world filenames (Screenshot*, *vacation*, *invoice*) without inspecting content.
- Positive: nested destinations like `Documents/Finance/Tax/{year}` create per-year buckets automatically as new files arrive.
- Positive: recursive scan lets the user organise a pre-existing folder tree without pre-flattening it.
- Negative: `{year}` uses mtime, not EXIF. Cloud-synced files may report the wrong year. Documented in `configuration.md` so the user does not assume chronological accuracy.
- Negative: matching policy change is a behaviour change for any pre-existing user config that relied on (theoretical) OR semantics. v0.1.0 had no such configs in the wild, and the default ruleset shipped with this change uses the new policy throughout.
- Negative: recursive scan can move a lot of files. The toggle is in the UI, default on, and the preview screen still requires a manual Confirm before execution, so no silent batch.
- Follow-ups: introduce EXIF date extraction when needed (out of scope; content-reading). Consider regex patterns alongside globs when users ask. Each new matcher type should be added to `configuration.md` and `domain/invariants/domain.md` §4b in the same change.