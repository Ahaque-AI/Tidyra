---
version: alpha
name: Tidyra
description: A calm, safety-first desktop organizer for reviewing file changes before they happen.
colors:
  teal: "#0F766E"
  mint: "#5EEAD4"
  warning: "#F59E0B"
typography:
  sans:
    fontFamily: "system-ui, sans-serif"
  mono:
    fontFamily: "ui-monospace, monospace"
rounded:
  DEFAULT: "0.5rem"
spacing:
  page-padding: "1rem"
components:
  button: {}
  card: {}
  checkbox: {}
---

# Tidyra Design System

## Overview

Tidyra is a product tool for people organizing real local files. Its job is
to make each consequence legible before it occurs. The product register is
quiet and practical: the teal folder mark is the distinctive signature while
the preview and actions remain familiar desktop controls. The runtime Flet
theme is the source of truth; this document records its brand colours and
system-theme behavior.

## Colors

Use teal (`#0F766E`) and mint (`#5EEAD4`) only for brand identity. Amber
(`#F59E0B`) signals that a folder-removal option is destructive but guarded.
System theme colours retain text and surface contrast in light and dark mode.

## Typography

Use the system UI font for readable file paths and actions. Use the mono role
only when a future technical surface needs aligned paths or values.

## Layout

Views use a 16 px page padding and one scroll owner. Preview details remain
visible above the final action, and destructive cleanup copy remains adjacent
to the button that performs it.

## Elevation & Depth

Cards group individual moves; no decorative elevation is needed beyond the
existing Flet card treatment.

## Shapes

Keep the existing rounded Flet controls and avoid novel shape variants.

## Components

Buttons use plain verbs. The empty-folder option starts unchecked, carries an
amber warning in preview, and changes the final action label to name removal.
The preview lists every folder that will be checked; the result reports how
many were actually removed. A directory that is not empty is not an error and
is left in place.

## Do's and Don'ts

- **Do:** make filesystem consequences visible before the user confirms them.
- **Do:** preserve system-theme readability and native keyboard behavior.
- **Don't:** hide destructive cleanup behind a generic confirmation label.
- **Don't:** use colour alone to explain that folder removal is optional.
