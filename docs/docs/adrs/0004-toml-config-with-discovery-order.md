# ADR-0004: TOML configuration with discovery order

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra ships with sensible default rules. Some users will want to override them locally without forking the package.

## Decision

The configuration format is TOML (stdlib `tomllib` in Python 3.11+). The discovery order, first-wins, is:

1. User config dir — `platformdirs.user_config_path("tidyra") / "rules.toml"`
   - Windows: `%APPDATA%\tidyra\rules.toml`
   - macOS: `~/Library/Application Support/tidyra/rules.toml`
   - Linux: `~/.config/tidyra/rules.toml`
2. `rules.toml` in the current working directory.
3. Built-in defaults shipped at `src/tidyra/resources/default_rules.toml`.

User rules override defaults by `name`. Conflicts between same-priority rules produce `SkipReason.RULE_CONFLICT` in the plan.

## Consequences

- Positive: zero-config out of the box; override without forking.
- Positive: `tomllib` is stdlib — no new dependency.
- Negative: discovery order is "first wins", which surprises users who expect merge. The order is documented in `configuration.md`.
- Negative: a wrong rule file in the user config dir silently shadows the defaults. Errors are surfaced at load time, not at run time.
- Follow-ups: a future config-validation CLI may pre-flight the TOML and surface mistakes before the user clicks "Scan".