# Configuration

Tidyra's only configuration is the rule list. Rules live in a single
TOML file. The app discovers the file automatically; you don't pass
paths or flags.

## Where Tidyra looks for rules

In order; the first file that exists wins:

1. **User config dir** — `rules.toml`
   - Windows: `%APPDATA%\tidyra\rules.toml`
   - macOS: `~/Library/Application Support/tidyra/rules.toml`
   - Linux: `~/.config/tidyra/rules.toml`
2. **Current working directory** — `./rules.toml`
3. **Built-in defaults** — shipped with the app at
   `src/tidyra/resources/default_rules.toml`.

To find the user config path on your machine:

```powershell
uv run python -c "from tidyra.infrastructure.configuration import get_config_service; print(get_config_service().default_config_path())"
```

## Schema

The file contains one or more `[[rule]]` tables.

```toml
[[rule]]
name = "raw-photos"
destination = "Photos/RAW"
extensions = [".cr2", ".nef", ".arw", ".dng"]
priority = 25

[[rule]]
name = "screenshots"
destination = "Screenshots"
name_patterns = ["Screenshot*", "Screen Shot*", "Capture*", "Snip*"]
priority = 30
```

| Field | Required | Type | Notes |
|---|---|---|---|
| `name` | yes | string | Stable identifier. Use it to override a built-in. |
| `destination` | yes | string | Directory relative to the scan root. Created if missing. Supports templates (see below). |
| `extensions` | no | list of strings | File extensions to match (with leading dot, lowercase). |
| `name_patterns` | no | list of strings | Glob patterns the file name must match (case-insensitive). E.g. `["Screenshot*", "*vacation*"]`. |
| `patterns` | no | list of strings | Legacy alias for `name_patterns`. New configs should use `name_patterns`. |
| `priority` | no | integer | Higher wins. Default `0`. Built-ins use `10`; catch-all `0`. |
| `always_matches` | no | boolean | Legacy. Equivalent to `name_patterns = ["*"]`. Kept so v0.1.0 configs still parse. Prefer `name_patterns` for new rules. |

## How matching works

A rule matches a file when **any** of its matchers hit:

- `always_matches = true` short-circuits to true.
- `extensions` lists file extensions; the file's extension (case-insensitive) must be in the list.
- `name_patterns` lists glob patterns; the file's name is matched against each pattern with `fnmatch` (case-insensitive).

When a rule sets **both** `extensions` and `name_patterns`, the file must satisfy **both** (intersection). This is the "name AND format together" semantic — a rule like

```toml
[[rule]]
name = "vacation-photos"
destination = "Photos/Trips/Vacation"
name_patterns = ["*vacation*", "*trip*", "*holiday*"]
extensions = [".jpg", ".jpeg", ".png", ".heic", ".mov", ".mp4"]
priority = 50
```

only fires when the file has one of those extensions **and** its name contains a vacation keyword. A plain `IMG_2024.jpg` does not match — it falls through to the lower-priority `photos-by-year` rule.

When a rule sets only one of the two, that single condition decides. (The legacy `always_matches` form bypasses both.)

## How rules combine

When more than one rule matches the same file:

- The rule with the highest `priority` wins. Tied rules produce `RULE_CONFLICT` and the file is skipped (the preview surfaces this).
- Within a priority tier, declared order in the TOML file is the tiebreaker.

## Destination templates

`destination` may contain template variables expanded from each file's mtime (last-modified timestamp) and name:

| Template | Source | Example (for a `tax-return.pdf` modified `2024-04-10`) |
|---|---|---|
| `{year}` | `mtime` as `%Y` | `2024` |
| `{month}` | `mtime` as `%m` (zero-padded) | `04` |
| `{stem}` | File name without its final extension | `tax-return` |
| `{ext}` | File extension without the leading dot (lowercase) | `pdf` |

Example: `Documents/Finance/Tax/{year}` resolves to `Documents/Finance/Tax/2024` for a 2024 file. **Note:** `{year}` and `{month}` use the file's `mtime` (last modified), not its true creation date. They are a useful proxy for organising photos and downloads, not a substitute for reading EXIF metadata.

Unknown templates are kept as literal text (`{unknown}`) so the user can see what they got wrong instead of a silent substitution. Folders that don't yet exist are created on demand by the executor.

## Built-in defaults

The shipped rule set covers the common Downloads use case:

| Rule | Destination | Priority | Matchers |
|---|---|---|---|
| `vacation-photos` | `Photos/Trips/Vacation` | 50 | `*vacation* \| *trip* \| *holiday*` (names) AND jpg/png/heic/mov/mp4 |
| `tax-documents` | `Documents/Finance/Tax/{year}` | 45 | `*tax* \| *1099* \| *w-2* \| *w2*` (names) |
| `invoices` | `Documents/Finance/Invoices` | 40 | `*invoice* \| *receipt* \| *bill*` (names) |
| `screenshots` | `Screenshots` | 30 | `Screenshot* \| Screen Shot* \| Capture* \| Snip*` (names) |
| `raw-photos` | `Photos/RAW` | 25 | `.cr2 .cr3 .nef .arw .dng .orf .rw2 .raw` (extensions) |
| `music` | `Music` | 10 | `.mp3 .wav .flac .aac .ogg .m4a .opus .wma .aiff` |
| `videos` | `Videos` | 10 | `.mp4 .mkv .mov .avi .webm .wmv .flv .m4v` |
| `archives` | `Archives` | 10 | `.zip .tar .gz .bz2 .xz .7z .rar .tgz` |
| `documents` | `Documents` | 10 | `.pdf .docx .txt .xlsx .pptx .odt .md .rtf .csv .epub` |
| `applications` | `Applications` | 10 | `.exe .msi .dmg .pkg .deb .rpm .apk .appimage` |
| `code` | `Code` | 10 | `.py .js .ts .go .rs .java ...` |
| `photos-by-year` | `Photos/{year}` | 5 | `.jpg .jpeg .png .webp .gif .bmp .tiff .heic` |
| `other` | `Misc` | 0 | catch-all (`name_patterns = ["*"]`) |

The exact list lives in `src/tidyra/resources/default_rules.toml` and is shipped with every install.

## Override a built-in rule

Drop a `rules.toml` in your user config dir with the same `name` and
the new fields. Tidyra replaces the built-in with your version.

```toml
# ~/.config/tidyra/rules.toml
[[rule]]
name = "images"  # (your own rule that shadows the built-in of the same name)
destination = "Photos"
extensions = [".jpg", ".jpeg", ".png", ".webp"]
priority = 20
```

This shadows the built-in `images` rule: photos now go to `Photos/`
instead of `Images/` and at a higher priority than the other built-ins.

## Add a new rule

Just add a new `[[rule]]` table. It is merged with the built-ins.

```toml
[[rule]]
name = "raw-photos"
destination = "Photos/RAW"
extensions = [".cr2", ".nef", ".arw", ".dng"]
priority = 25
```

Higher priority than the generic `photos-by-year` (`5`), so `.cr2` files
land in `Photos/RAW/` even though they share an extension with the year
buckets.

A name-and-format example:

```toml
[[rule]]
name = "receipts-by-year"
destination = "Documents/Finance/Receipts/{year}"
name_patterns = ["*receipt*"]
extensions = [".pdf", ".png", ".jpg", ".heic"]
priority = 35
```

Only files that contain `receipt` in the name AND have one of those
extensions land here. The `{year}` template automatically creates a new
folder per year as new receipts arrive.

## Catch-all

The `other` rule uses `priority = 0` and `name_patterns = ["*"]`, so it
catches anything no other rule picked. If you'd rather skip unmatched
files entirely, override `other` to point at a no-op destination:

```toml
[[rule]]
name = "other"
destination = "_REVIEW_ME"
priority = 0
name_patterns = ["*"]
```

Or replace it with a placeholder and clean up manually later — files
that match no rule are flagged `UNMATCHED` in the preview and not
moved. Use this when you'd rather make decisions manually than have
Tidyra route unknown files to `Misc/`.

## What happens with no config file

If you don't write a `rules.toml`, the built-in defaults are used. The
app works out of the box.

## Validation errors

Bad TOML raises a clear error at startup. Common mistakes:

- `name` or `destination` missing → "rule entry missing string 'name'"
- `extensions` is not a list → "rule <name> 'extensions' must be a list"
- `name_patterns` is not a list → "rule <name> 'name_patterns' must be a list"
- `priority` is not an integer → "rule <name> 'priority' must be an integer"

If you see one of these, fix the file and relaunch.

## Recursion

The home view has a "Recurse into subfolders" toggle (default: on). When
on, Tidyra walks every regular file under the chosen root and preserves
the relative subfolder structure inside each rule's destination. So
`Downloads/2024/photo.jpg` (with the `photos-by-year` rule) lands at
`Photos/2024/photo.jpg`, and `Downloads/taxes/2024/invoice.pdf` (with
a hypothetical tax+invoice rule) lands at the right place with the
original `taxes/2024/` structure preserved inside.

When off, only the direct children of the chosen root are scanned — the
v0.1.0 behaviour. The toggle is per-scan; the user's preference does
not persist between launches.

Recursion does **not** change safety. `PlanValidator` still rejects
moves whose destinations are *inside* another move's source path, so a
recursive scan cannot arrange a folder into a destination we are
about to move.
