# ADR-0010: Date and format routing

- Status: Superseded by ADR-0012
- Date: 2026-09-03
- Deciders: Abdul Haque, Mavis
- Context: Users need predictable date folders, separate folders for formats such as PNG and JPEG, and explicit relevance rules without an LLM.

## Decision

Superseded. ADR-0012 replaces format-level built-in folders with regex topic routing and a lexically sortable date label.

## Consequences

- Positive: every built-in route follows `date → category → format` with a visible, reproducible path.
- Positive: users can express subject relevance with filename globs and allowed formats alone.
- Negative: last-modified time is not a reliable download or creation date, so Tidyra does not label it as one.
- Follow-ups: add a separate creation-date source only if it can be specified consistently across supported filesystems.
