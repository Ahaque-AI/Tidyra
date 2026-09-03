# ADR-0014: Named topic captures

- Status: Accepted
- Date: 2026-09-03
- Deciders: Abdul Haque, Mavis
- Context: Generic `Documents`, `Images`, and `Misc` buckets lose meaning when several files belong to a named application or project.

## Decision

Support `topic_regex`, a case-insensitive regular expression with a required named `topic` capture. A matching rule may use `{topic}` in its destination to group related files, such as `Applications/arango`. The capture is sanitized for safe path use; no topic is inferred from content or an LLM.

## Consequences

- Positive: users can create meaningful per-application or per-project folders with one deterministic rule.
- Positive: extension filters can keep unrelated files out of the group while the destination stays format-agnostic.
- Negative: the user must define the product/project name or a deliberately narrow regex.
- Follow-ups: do not add fuzzy similarity or content classification without a separate ADR.
