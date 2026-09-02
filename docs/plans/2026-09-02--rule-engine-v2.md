# Plan — Rule engine v2 (names + extensions + nested destinations + recursion)

**Date:** 2026-09-02
**Status:** Approved (per user request in this session)
**Author:** Mavis (drafted), Abdul Haque (decision)

## Goal

Make Tidyra smarter about *which files match which rule* and *where they go*, with three concrete improvements:

1. **Match on file names**, not just extensions. Today a rule like `*.jpg` matches because of the extension; a rule like `Screenshot*` should match because of the name. Both should be expressible.
2. **Create nested destinations**. Today every rule points at a flat folder under the root. Some classes of files want `Photos/By-Year/2024/Q1/` or `Documents/Finance/Invoices/`. The user wants deeper, smarter folders.
3. **Recurse through subdirectories**. Today the scan is one level deep. The user wants Tidyra to walk subfolders and re-organise them too.

We do not read file contents (per the user: "Not seeing content but can match names and formats together"). All classification uses the file name, extension, and stat() metadata.

## Non-goals (this change)

- EXIF date extraction for photos.
- Regex matching (glob is enough; users can suggest regex later via ADR).
- Date-range buckets ("This Week", "This Month") — would need a clock and the user asked for nested folders, not "smart" buckets.
- Undo. Still out of scope.
- Per-rule recursion depth. The recursion is one fixed flag.

## Design

### Layer boundary

The change touches:

| Layer | What changes |
|---|---|
| `domain/models.py` | Add `mtime: float` to `FileEntry` (for `{year}` / `{month}` substitution). |
| `domain/rules.py` | Make `patterns` active (case-insensitive glob). Drop `always_matches` (now redundant with `patterns=["*"]`). Add a `substitute_destination(destination, entry) -> str` helper that resolves `{year}`, `{month}`, `{ext}`, `{name}`. |
| `domain/strategies.py` | `_classify()` calls the substitution helper so each move gets the rendered destination. Patterns participate in matching. |
| `infrastructure/filesystem.py` | `FileSystem.scan(root, *, recurse: bool = False) -> Sequence[FileEntry]` — recursive walk returns *relative paths* under root, but each entry still records its absolute `path` so the executor moves the right file. |
| `infrastructure/configuration.py` | Parser accepts `patterns` (already does; no behaviour change to existing TOML). Drop `always_matches` support? **Keep it** for backward-compat — the bundled defaults no longer use it. |
| `application/services.py` | `OrganizeService.scan` forwards the new `recurse` flag. |
| `application/organize.py` / `controller.py` | Default `recurse=True` for the user-facing path (since the user asked for it), but expose a flag in the UI so the user can opt out per scan. |
| `resources/default_rules.toml` | Bigger, smarter default set, with patterns + nested destinations. The catch-all uses `patterns = ["*"]` instead of `always_matches`. |

### Substitution syntax

In any `destination` string:

| Template | Substitutes | Example |
|---|---|---|
| `{year}` | Year from the file's `mtime` (`%Y`) | `Photos/By-Year/{year}` → `Photos/By-Year/2024` |
| `{month}` | Month from the file's `mtime` (`%m`) | `Photos/By-Year/{year}/{month}` → `Photos/By-Year/2024/03` |
| `{ext}` | Lowercase file extension without leading dot | `{ext}/...` → `pdf/...` |
| `{name}` | The file's stem (name without extension) | rare; for renaming |

Unknown templates stay as literal text so users see what they got wrong instead of a silent failure.

### Safety

Recursive scan does not change PlanValidator's guarantees:

- `OUTSIDE_ROOT` still rejects anything that escapes the chosen root.
- `DESTINATION_EXISTS` still rejects silent overwrites.
- `NESTED_DESTINATION` still rejects two moves that nest. With recursion, we must also reject moves where the destination is *inside an existing source path* (otherwise we'd move a file into a folder we're about to move). The validator already covers this when the source-destination relationship is set up correctly; add a clarifying test case.

### Defaults

Roughly the new shape of `default_rules.toml`:

```toml
[[rule]]                       # priority: very high so vacation photos beat the generic photo rule
name = "vacation-photos"
destination = "Photos/Trips/Vacation"
name_patterns = ["*vacation*", "*trip*", "*holiday*"]
extensions = [".jpg", ".jpeg", ".png", ".heic", ".mov", ".mp4"]
priority = 50

[[rule]]                       # screenshots are easy to detect by name
name = "screenshots"
destination = "Screenshots"
name_patterns = ["Screenshot*", "Screen Shot*", "Capture*", "Snip*"]
priority = 30

[[rule]]                       # invoices go in finance, regardless of file type
name = "invoices"
destination = "Documents/Finance/Invoices"
name_patterns = ["*invoice*", "*receipt*", "*bill*"]
priority = 40

[[rule]]                       # tax docs go in a year-bucketed folder
name = "tax-documents"
destination = "Documents/Finance/Tax/{year}"
name_patterns = ["*tax*", "*1099*", "*w-2*", "*w2*"]
priority = 45

[[rule]]                       # raw photos
name = "raw-photos"
destination = "Photos/RAW"
extensions = [".cr2", ".nef", ".arw", ".dng", ".raw"]
priority = 25

[[rule]]                       # generic photos by year (mtime proxy)
name = "photos-by-year"
destination = "Photos/Photos-{year}"
extensions = [".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif"]
priority = 5

[[rule]]
name = "images"
destination = "Photos"
extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg", ".heic"]
priority = 1

... (existing rules for documents, music, videos, archives, applications, code) ...

[[rule]]                       # catch-all uses patterns = ["*"]
name = "other"
destination = "Misc"
name_patterns = ["*"]
priority = 0
```

Top-priority rules (high number) win when they match; everything else falls through.

### Recursion semantics

`scan(root, recurse=True)` walks every regular file under `root` and returns it as a `FileEntry`. The destination is computed as `root / <rule destination> / <entry relative path under root>` — preserving the *relative structure* beneath the root. So:

- `Downloads/2024/screenshot.png` → `Photos/2024/Screenshots/screenshot.png` (no, that's wrong)

Wait — re-think. If a file is at `Downloads/subfolder/file.txt`, do we want:
a) `SubfolderName/rule-name/file.txt` — preserving the original subfolder
b) `rule-name/subfolder-name/file.txt` — flat grouping, but the original subfolder stays as a label

I'll go with (b): `Downloads/subfolder/foo.jpg` → `Photos/subfolder/foo.jpg`. Reasoning: by the time the user runs Tidyra, the subfolder is part of the metadata we want to preserve. The rule puts everything in the right top-level folder; the original subfolder structure shows up inside it.

Actually, even simpler and less surprising: relocate to `root / <rule destination> / entry.name` — i.e., move *into* the top-level rule folder, regardless of where the file lived originally. That's how `Downloads/foo.jpg` and `Downloads/subfolder/foo.jpg` both go to `Photos/foo.jpg` and `Photos/subfolder/foo.jpg` respectively (if the subfolder is preserved). The original subfolder structure is preserved as part of the relative path.

That's safer too — we never destroy the original subfolder structure, just relocate it under a rule-destined top-level folder.

Plan for the move:
- File at `root/sub1/sub2/foo.jpg`
- Rule destination: `Photos`
- Move target: `root/Photos/sub1/sub2/foo.jpg`

This requires creating intermediate directories during move, which `shutil.move` already handles.

### UI

The home view gets a "recurse subfolders" checkbox/toggle. Default: ON. When OFF, behaviour matches the old one-level scan.

## Steps

1. **Models** — add `mtime` to `FileEntry`. Update `LocalFileSystem._build_entry`.
2. **Rules** — implement pattern matching, substitution helper. Drop `always_matches` from defaults.
3. **Strategy** — wire substitution into `_classify()`.
4. **Filesystem** — add `recurse` flag to `scan`.
5. **Application** — pass `recurse=True` from `OrganizeService.scan` by default. Add `recurse` to UI flow.
6. **Presentation** — add a checkbox or Switch to `home_view`. Update state to track `recurse` preference.
7. **Defaults** — rewrite `default_rules.toml` with the new richer rule set.
8. **Tests** — write a few mental tests. The project ships without a test runner yet, so add at least inline `__main__` smoke tests.
9. **Docs** — update `docs/docs/tooling/configuration.md` with the new pattern syntax; document templates; add an ADR-0008.

## Verification

- `uv run ruff check .` clean.
- `uv run mypy src` clean.
- `uv run python -c "..."` smoke tests:
  - A rule with `name_patterns = ['Screenshot*']` matches a file named `Screenshot 2024-01-01.png`.
  - A rule with `destination = 'Photos/{year}'` resolves to `Photos/2024` for a file whose mtime is in 2024.
  - Recursive scan returns nested files.
  - PlanValidator still rejects nested destinations.
- Manual: `uv run tidyra`, pick a folder with mixed files, scan, inspect the preview, verify destinations match expectations.

## Files changed

- `src/tidyra/domain/models.py` (FileEntry.mtime)
- `src/tidyra/domain/rules.py` (pattern matching, substitution)
- `src/tidyra/domain/strategies.py` (substitution in _classify)
- `src/tidyra/infrastructure/filesystem.py` (recurse flag)
- `src/tidyra/application/services.py` (forward recurse)
- `src/tidyra/presentation/views/home.py` (recurse checkbox)
- `src/tidyra/presentation/state.py` (recurse in UIState)
- `src/tidyra/presentation/controller.py` (pass recurse through)
- `src/tidyra/resources/default_rules.toml` (full rewrite)
- `docs/docs/tooling/configuration.md` (pattern syntax + templates)
- `docs/docs/adrs/0008-smarter-rule-engine.md` (capture this decision)
- `docs/docs/adrs/index.md` (row)
- `CHANGELOG.md` ([Unreleased] entry)
- `README.md` (mention the new capabilities)

## Dependencies

- None. Pure stdlib + existing deps. `fnmatch` for pattern matching.

## Common issues

- Pattern matching must be case-insensitive — Windows is case-insensitive at the FS level, macOS users often have mixed-case filenames, and we want consistent rules across platforms.
- Date substitution uses `mtime`. Files moved between systems (e.g., via cloud sync) may have a creation mtime, not a content timestamp. Document this clearly.
- Recursive scan can move a lot of files. The UI must show a count before confirm and surface safety reminders.
- Pre-existing `always_matches` user configs still work for one release; we'll log a deprecation hint but keep parsing them.
