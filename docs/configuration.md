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
name = "images"
destination = "Images"
extensions = [".jpg", ".jpeg", ".png", ".webp"]
priority = 10
```

| Field | Required | Type | Notes |
|---|---|---|---|
| `name` | yes | string | Stable identifier. Use it to override a built-in. |
| `destination` | yes | string | Directory relative to the scan root. Created if missing. |
| `extensions` | no | list of strings | File extensions to match (with leading dot, lowercase). Ignored when `always_matches` is true. |
| `patterns` | no | list of strings | Reserved for future glob support. |
| `priority` | no | integer | Higher wins. Default `0`. Built-ins use `10`. |
| `always_matches` | no | boolean | If true, the rule matches every file. Used for catch-alls. |

## How rules combine

When multiple rules match the same file:

- The rule with the highest `priority` wins.
- If two rules at the same priority both match, the file is marked
  `RULE_CONFLICT` and skipped. The preview will tell the user.

## Built-in defaults

The shipped rule set covers the common Downloads use case:

| Rule | Destination | Priority | Extensions |
|---|---|---|---|
| `images` | `Images` | 10 | `.jpg .jpeg .png .webp .gif .bmp .tiff .svg .heic` |
| `documents` | `Documents` | 10 | `.pdf .docx .txt .xlsx .pptx .odt .md .rtf .csv .epub` |
| `music` | `Music` | 10 | `.mp3 .wav .flac .aac .ogg .m4a .opus .wma` |
| `videos` | `Videos` | 10 | `.mp4 .mkv .mov .avi .webm .wmv .flv .m4v` |
| `archives` | `Archives` | 10 | `.zip .tar .gz .bz2 .xz .7z .rar .tgz` |
| `applications` | `Applications` | 10 | `.exe .msi .dmg .pkg .deb .rpm .apk .appimage` |
| `code` | `Code` | 10 | `.py .js .ts .go .rs .java ...` |
| `other` | `Misc` | 0 | (catch-all; `always_matches = true`) |

## Override a built-in rule

Drop a `rules.toml` in your user config dir with the same `name` and
the new fields. Tidyra replaces the built-in with your version.

```toml
# ~/.config/tidyra/rules.toml
[[rule]]
name = "images"
destination = "Photos"
extensions = [".jpg", ".jpeg", ".png", ".webp"]
priority = 20
```

This overrides the built-in `images` rule: photos now go to `Photos/`
instead of `Images/` and at a higher priority than the other built-ins.

## Add a new rule

Just add a new `[[rule]]` table. It will be merged with the built-ins.

```toml
[[rule]]
name = "raw-photos"
destination = "Photos/RAW"
extensions = [".cr2", ".nef", ".arw", ".dng"]
priority = 20
```

Higher priority than `images` (`10`), so `.cr2` files win even though
`.cr2` isn't in the built-in `images` list.

## Catch-all

The `other` rule uses `always_matches = true` and `priority = 0`, so it
catches anything no other rule picked. If you'd rather skip unmatched
files entirely, drop the `other` rule from your user config:

```toml
# Empty file with just one rule removed by name override
# (delete the 'other' rule by overriding it to do nothing)
```

Or replace it with a no-op destination you can clean up manually:

```toml
[[rule]]
name = "other"
destination = "_REVIEW_ME"
priority = 0
always_matches = true
```

## What happens with no config file

If you don't write a `rules.toml`, the built-in defaults are used. The
app works out of the box.

## Validation errors

Bad TOML raises a clear error at startup. Common mistakes:

- `name` or `destination` missing → "rule entry missing string 'name'"
- `extensions` is not a list → "rule <name> 'extensions' must be a list"
- `priority` is not an integer → "rule <name> 'priority' must be an integer"

If you see one of these, fix the file and relaunch.
