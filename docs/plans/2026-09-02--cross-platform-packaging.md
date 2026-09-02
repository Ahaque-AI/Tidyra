# Plan — Cross-platform packaging (macOS / Windows / Linux)

**Date:** 2026-09-02
**Status:** Approved (per user request in this session)
**Author:** Mavis (drafted), Abdul Haque (decision)

## Goal

Ship Tidyra as installable executables on Windows, macOS, and Linux. The build must be reproducible from the source tree and the binaries must be downloadable by users without a working Python install.

## Non-goals

- App store submission (we are not in Phase 4 of the roadmap yet).
- Auto-update channel.
- Code signing on macOS/Windows (deferred — see Open Questions).
- Mobile / iOS / Android (separate effort; not part of this change).

## The pattern

**Source in git. Binaries in GitHub Releases. CI does the building.**

This is the standard, low-surprise arrangement:

- The repository tracks the Python source, the Flet app entry point, the rules, the docs, the icon source (`tidyra-logo.svg`), and a generated icon set under `assets/icons/`.
- A GitHub Actions workflow `.github/workflows/release.yml` builds on every pushed tag of the form `v*.*.*`. Three matrix jobs (`windows-latest`, `macos-latest`, `ubuntu-latest`) each produce a platform-native artifact.
- A fourth job collects the three artifacts and creates a GitHub Release with them attached.
- Users download the binary that matches their OS from the Releases page. The README points there.

The repo does **not** store `.exe` / `.dmg` / `.AppImage` files in git. Git is for source. Releases are for binaries.

## Tooling — `flet build`

`flet build` is the Flet-native packaging tool. It wraps Flutter under the hood, which is heavy (≈ 500 MB first build) but gives us proper native bundles per platform:

| Platform | `flet build` subcommand | Output |
|---|---|---|
| Windows | `flet build windows` | A directory containing `tidyra.exe`, plus the supporting DLLs and Python runtime. Zip-distributable. |
| macOS   | `flet build macos`   | A `.app` bundle that can be zipped or wrapped in a `.dmg`. |
| Linux   | `flet build linux`   | An `.AppImage` (single-file executable, no install). |

Important constraints:

- **You cannot easily cross-compile.** A Windows `.exe` must be built on Windows. A macOS `.app` must be built on macOS (the `.icns` format and macOS bundle conventions are not portable). This is why the CI does the building.
- **Code signing is optional in this phase.** Unsigned Windows binaries trigger SmartScreen warnings; unsigned macOS binaries trigger Gatekeeper warnings. We accept these warnings for now and document them. Code signing becomes mandatory when we ship to a wide audience — see Open Questions.

## Icon set

`flet build` looks for icons in a per-platform location:

- macOS: `assets/icons/app_icon.icns` (or a PNG set under `macos/Runner/Assets.xcassets/AppIcon.appiconset/`).
- Windows: `assets/icons/app_icon.ico` (we already have this from the brand batch).
- Linux: `assets/icons/icon.png` (typically 256×256 or 512×512).

We extend `tools/build_icon.py` to produce **all** of these from the brand source `tidyra-logo.svg`:

1. A multi-size PNG set (16, 32, 48, 64, 128, 256, 512, 1024) under `assets/icons/png/`.
2. The `.ico` (existing) — Windows title bar + build icon.
3. On macOS CI, `iconutil` converts the PNG set to `.icns`.

The SVG stays the brand source of truth. The build script regenerates everything else deterministically.

## GitHub Actions workflow

`.github/workflows/release.yml`:

- **Trigger**: `push` of a tag matching `v[0-9]+.[0-9]+.[0-9]+` (e.g. `v0.2.0`).
- **Manual trigger**: `workflow_dispatch` for ad-hoc builds (does not create a release).
- **Matrix**:
  - `windows-latest` → `flet build windows` → zips `dist/windows/` → `tidyra-windows-x64.zip`
  - `macos-latest` (Apple Silicon by default; an Intel runner can be added) → `flet build macos` → zips the `.app` → `tidyra-macos-arm64.zip`; on this runner, `iconutil` converts the PNG set to `app_icon.icns`
  - `ubuntu-latest` → `flet build linux` → `tidyra.AppImage`
- **Release job**: downloads all three artifacts and uses `softprops/action-gh-release@v2` to create a GitHub Release with the tag name as the title, the changelog excerpt as the body, and the three artifacts attached.

We also add `.github/workflows/ci.yml` for everyday PRs: runs ruff + mypy + smoke-test script on Python 3.11 / 3.12 / 3.13. No builds, no artifacts.

## Local builds

For the user's local testing (Windows):

```powershell
uv run flet build windows --product Tidyra --org dev.abdulhaque --bundle-id dev.abdulhaque.tidyra --copyright "MIT License" --project tidyra
```

This downloads Flutter the first time and produces `dist/windows/tidyra.exe`. The first build is slow (5–10 min); subsequent builds reuse the cache.

For Linux:

```bash
uv run flet build linux --product Tidyra --org dev.abdulhaque --bundle-id dev.abdulhaque.tidyra --project tidyra
```

For macOS (must be on a Mac):

```bash
uv run flet build macos --product Tidyra --org dev.abdulhaque --bundle-id dev.abdulhaque.tidyra --project tidyra
```

## Files changed

| Path | Purpose |
|---|---|
| `tools/build_icon.py` | Extended to generate multi-size PNGs in addition to the `.ico`. |
| `assets/icons/png/*.png` | Generated PNG icons (16..1024). |
| `assets/icons/tidyra-icon.ico` | Move existing `.ico` here (alongside PNGs for clean handoff to `flet build`). |
| `.github/workflows/release.yml` | The release pipeline. |
| `.github/workflows/ci.yml` | The everyday CI (lint + type check + smoke test). |
| `docs/docs/adrs/0009-cross-platform-packaging.md` | Capture the architectural decision. |
| `docs/docs/processes/invariants/processes.md` | Document the release flow (5a). |
| `docs/docs/tooling/invariants/tooling.md` | Document `flet build` invocations. |
| `README.md` | Link the Releases page in the Quick Start. |
| `CHANGELOG.md` | Note the build pipeline under `[Unreleased]`. |
| `pyproject.toml` | Package the PNG assets alongside the existing TOML/SVG/ICO. |

## Verification

- `uv run ruff check .` and `uv run mypy src tools` clean (already passing).
- Local `uv run python tools/build_icon.py` regenerates the full icon set.
- Local `uv run flet build windows --product Tidyra --project tidyra --org dev.abdulhaque` produces a runnable `.exe`. (First build pulls Flutter; later builds are faster.)
- The CI workflow YAML is valid (`actionlint` or by pushing the a test branch).
- The `tools/smoke_rules.py` smoke test still passes after the icon-asset refactor.

## Open questions (not blocking)

- **Code signing.** For Windows, a code-signing cert costs roughly $70/year and removes the SmartScreen warning. For macOS, an Apple Developer account ($99/year) and a notarised bundle is required for friction-free distribution. Neither is in scope for this batch. ADR-0009 captures the decision to ship unsigned; revisit when we have a wide-distribution audience.
- **Universal macOS binary.** Building for both arm64 and x86_64 from a single artifact requires two macOS runners and `lipo`. The current matrix produces arm64 only; adding x86_64 is a follow-up if needed.
- **PyInstaller fallback.** Some teams prefer PyInstaller because it produces smaller binaries. For Flet apps, `flet build` is the official path. If we hit a Flutter pain point, PyInstaller is the documented fallback.
- **Linux package formats.** `flet build linux` produces AppImage. We can extend the matrix to produce `.deb` and `.rpm` as well. Out of scope for the first cut.

## Dependencies

- None at runtime.
- `flet-cli` (already installed as a Flet dependency) provides `flet build`.
- For the CI: standard GitHub-hosted runners (windows-latest, macos-latest, ubuntu-latest). No self-hosted runners needed.
- For the macOS `.icns`: macOS's built-in `iconutil` (preinstalled on macOS-latest runners).
- For uploading the GitHub Release: `softprops/action-gh-release@v2` (a free, widely used action).