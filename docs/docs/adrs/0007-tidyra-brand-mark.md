# ADR-0007: Tidyra brand mark — folder with three tidied file cards

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra shipped with the Flet default icon. The brand needs an ownable mark that reads at favicon size and at full header size, works in light and dark mode, and communicates the product's purpose.

## Decision

The Tidyra mark is a folder silhouette containing three tidied file cards:

```
┌──────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ │   deep teal  #0F766E  — folder body
│ ▔▔▔▔▔▔▔▔▔▔            │
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔        │   light teal #5EEAD4  — file cards
└──────────────────────┘
```

The single source of truth is `src/tidyra/resources/tidyra-logo.svg`. It is loaded at runtime via `tidyra.presentation.brand.logo_path()` (see ADR-0006). The same SVG drives:

1. `page.window.icon` — set once in `presentation/app.py:main`.
2. The home view header brand row (`views/home.py`).
3. Any future favicon, README hero, or marketing export.

Palette: `#0F766E` (folder body), `#5EEAD4` (file cards). No other colours ship in the brand mark.

## Consequences

- Positive: one SVG drives every surface — no drift.
- Positive: SVG scales from 16 px favicon to ≥ 64 px header without raster artefacts.
- Positive: deep teal reads well on both light and dark backgrounds.
- Negative: raster platforms (Windows .ico, macOS .icns) require an export step. Documented in [frontend/invariants/frontend.md §9](../frontend/invariants/frontend.md#9-brand-mark-palette).
- Negative: changing the palette later is a brand decision, not a code decision — it requires a new ADR.
- Follow-ups: README hero image, favicon, and PyInstaller window-icon export should all derive from this SVG. Any divergence is a regression and must be fixed in the same change that introduces the divergence.