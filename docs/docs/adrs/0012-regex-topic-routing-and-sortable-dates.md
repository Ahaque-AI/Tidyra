# ADR-0012: Regex topic routing and sortable dates

- Status: Accepted
- Date: 2026-09-03
- Deciders: Abdul Haque, Mavis
- Context: Format-level folders created too much structure. Users want folders based on explicit filename topics and dates that sort chronologically in ordinary file viewers.

## Decision

Add `name_regexes` as case-insensitive, deterministic filename matchers. Built-in topic rules use regexes and route to `date → topic/category`, never to a format-level folder. The `{date}` template renders as `YYYY-MM-DD — D Month YYYY`, so alphabetical sorting is chronological while the date remains readable.

## Consequences

- Positive: invoices, taxes, screenshots, and trips route by explicit filename topic without an LLM.
- Positive: generic categories remain simple and do not create PNG, JPEG, PDF, or similar subfolders.
- Negative: regexes recognize only the phrases users write; they do not infer a topic from file contents.
- Follow-ups: preserve `name_patterns` for simple glob rules; do not add semantic or content-based classification without a separate ADR.
