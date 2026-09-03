# ADR-0013: Date-folder modified times

- Status: Accepted
- Date: 2026-09-03
- Deciders: Abdul Haque, Mavis
- Context: Moving files creates or updates folders at the current time, which prevents file viewers from sorting date folders by their represented dates.

## Decision

After moving files into a date-first destination, set the date folder's modified time to the newest source-file timestamp routed to that folder. Do not modify folder creation times.

## Consequences

- Positive: Explorer can sort date folders by **Date modified** descending without treating every new folder as current.
- Positive: timestamp changes apply only to date folders Tidyra created or used in the visible plan.
- Negative: the date-folder modified time represents the newest routed file, not the wall-clock time of the move.
- Follow-ups: do not change creation timestamps; they are platform-specific and not a reliable cross-platform contract.
