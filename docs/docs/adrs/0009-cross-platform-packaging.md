# ADR-0009: Cross-platform packaging — `flet build` + GitHub Actions releases

- Status: Accepted
- Date: 2026-09-02
- Deciders: Abdul Haque, Mavis
- Context: Tidyra needs to ship as installable executables on Windows, macOS, and Linux so users without a working Python install can use it.

## Decision

Three concrete choices:

1. **`flet build` for packaging.** The official Flet packaging tool wraps Flutter under the hood and produces per-platform native bundles (`flet build windows` → `.exe` + DLLs, `flet build macos` → `.app` bundle, `flet build linux` → `.AppImage`). PyInstaller is the documented fallback if `flet build` ever stops meeting our needs, but is not the chosen path.
2. **Source in git, binaries in GitHub Releases.** We do not commit `.exe` / `.app` / `.AppImage` to the repository. Every `v*.*.*` tag push triggers `.github/workflows/release.yml`, which builds the three artifacts on `windows-latest` / `macos-latest` / `ubuntu-latest` in parallel and attaches them to a GitHub Release. Users download from the Releases page.
3. **Code signing deferred.** Unsigned Windows binaries trigger SmartScreen; unsigned macOS binaries trigger Gatekeeper. We accept those warnings for the alpha phase. Revisit when we have a wide-distribution audience — see Open Questions below.

The icon set is procedurally generated from `src/tidyra/resources/tidyra-logo.svg` (the brand source of truth) by `tools/build_icon.py` (stdlib only, no Pillow). The script writes:

- `assets/icons/tidyra-icon.ico` — Windows build icon.
- `assets/icons/icon.png` — Linux build icon.
- `assets/icons/png/tidyra-icon-{16..1024}.png` — multi-size PNG set; the macOS runner assembles them into an `.iconset` and runs `iconutil -c icns` to make `tidyra.icns`.
- `src/tidyra/resources/tidyra-icon.ico` — packaged with the wheel for runtime `page.window.icon`.

## Consequences

- Positive: one packaging tool, three platforms, identical metadata (`--product Tidyra --org dev.abdulhaque --bundle-id dev.abdulhaque.tidyra`).
- Positive: releases are reproducible from any tagged commit. CI does the heavy lifting; users get prebuilt binaries.
- Positive: source stays clean — `dist/` is gitignored, no 50-MB binaries ever land in git.
- Negative: first `flet build` per machine pulls the Flutter SDK (≈ 500 MB). Once cached, subsequent builds are fast.
- Negative: macOS builds require a macOS runner. We cannot cross-compile. Code signing on macOS requires an Apple Developer account — see Open Questions.
- Negative: unsigned Windows builds trigger a SmartScreen warning that requires extra clicks to dismiss. Unsigned macOS builds need a manual `xattr -d com.apple.quarantine` on first launch.
- Follow-ups: each new icon size or theme variant regenerates assets and triggers a CI smoke run; the `tools/build_icon.py` script is the single regeneration point.

## Open Questions (not blocking, captured for follow-up ADRs)

- **Code signing.** Windows EV/Authenticode cert (~$70/yr minimum) and Apple Developer account ($99/yr) both unlock friction-free distribution. Add when we ship to a wide audience or want to publish on app stores. Until then, document the SmartScreen / Gatekeeper warnings in the README.
- **Universal macOS binary.** Building for both arm64 and x86_64 from a single artifact requires two macOS runners and `lipo`. The current matrix produces arm64 only; add x86_64 if Intel-Mac users complain.
- **PyInstaller fallback.** Smaller binaries, but loses the per-platform polish. Switch only if Flutter pain points emerge.
- **Linux package formats.** `flet build linux` produces AppImage. We can extend the matrix to also produce `.deb` and `.rpm` if needed.

## See also

- Plan: `docs/plans/2026-09-02--cross-platform-packaging.md`
- Implementation: `tools/build_icon.py`, `.github/workflows/release.yml`, `.github/workflows/ci.yml`
- Updated docs: `docs/docs/tooling/invariants/tooling.md` §10, `docs/docs/processes/invariants/processes.md` §5
- Brand source: `src/tidyra/resources/tidyra-logo.svg`