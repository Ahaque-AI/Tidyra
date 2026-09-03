# ADR-0015: Meaningful default destinations

- Status: Accepted
- Date: 2026-09-03
- Deciders: Abdul Haque, Mavis
- Context: Broad default folders such as `Documents`, `Code`, and `Misc` hide why files belong together and create cleanup work after organization.

## Decision

Use high-priority filename rules for recognizable projects and document purposes, route source files into language-family folders, and send genuinely ambiguous files to `Needs Review` instead of assigning a false category. Remove broad application-name guessing from the defaults; known products need narrow rules. Keep classification deterministic and filename-based; do not infer topics from opaque identifiers or file contents.

## Consequences

- Positive: recognizable ArangoDB, coursework, resume, research, report, and finance files land in useful nested folders.
- Positive: source code folders state what kind of code they contain.
- Positive: uncertainty is visible and actionable rather than hidden in `Misc`.
- Positive: arbitrary configuration files no longer become application folders based on their first filename token.
- Negative: opaque filenames still require manual review unless the user adds a rule for their naming convention.
- Follow-ups: add narrow user rules when a repeated filename convention proves stable; content inspection or LLM classification requires a separate decision.
