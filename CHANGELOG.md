# Changelog

All notable changes to Tidyra are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial scaffold: domain layer (models, rules, plans, strategies),
  infrastructure (filesystem + TOML config), application services
  (scanner, organizer, executor), and Flet presentation layer (home,
  preview, results views; folder picker, file list, plan view, result
  view components).
- Built-in default rules covering Images, Documents, Music, Videos,
  Archives, Applications, Code, and a `Misc/` catch-all.
- Configuration discovery: user config dir → CWD `rules.toml` → built-in
  defaults.
- Safety enforcement: no deletion, no silent overwrite, no symlink
  following, no moves outside the chosen root.
- `OrganizationStrategy` Protocol with `RuleBasedStrategy` implementation
  ready for a future `LLMStrategy` to plug into.

## [0.1.0] - 2026-09-02

### Added
- First public release of the initial scaffold.

[Unreleased]: https://github.com/abdulhaque/tidyra/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/abdulhaque/tidyra/releases/tag/v0.1.0
