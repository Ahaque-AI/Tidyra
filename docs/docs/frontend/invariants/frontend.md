# Frontend rules — Flet presentation layer

## 1. Views are thin

A view function signature is always `def <name>_view(app: TidyraApp) -> ft.Control`. Inside the function:

- Read view-local data from `app.state`.
- Hand off to `app.<verb>()` for actions (`app.scan()`, `app.organize()`, `app.back_home()`).
- Render the returned state.

No filesystem calls, no `PlanValidator` calls, no rule lookups, no logging. If a view wants a value that isn't already on `app.state`, push it onto the state in the controller, not the view.

## 2. Components take callbacks

Components are reusable Flet controls. They take callbacks (`on_pick`, `on_click`, …) and never import the controller. The view that owns a component wires the callback. This keeps components easy to render in isolation.

```python
def folder_picker(*, path: str | None, on_pick: Callable[[str], None]) -> ft.Control:
    ...
```

## 3. Resolve brand assets via `presentation.brand`

The logo is the only brand asset today. Do not hard-code `src/tidyra/resources/tidyra-logo.svg` from a view or a component. Use:

```python
from tidyra.presentation.brand import logo_path
ft.Image(src=str(logo_path()), width=36, height=36, fit=ft.BoxFit.CONTAIN)
```

This makes the asset portable under editable installs (`uv run`) and frozen wheels alike.

## 4. Window icon and window title

`page.window.icon` and `page.title` are set once, in `app.py:main`. Adding a new window attribute? Set it there — do not duplicate the page-config calls in views.

### Window icon is the `.ico`, not the SVG

Flet 0.86's `Window.icon` source says verbatim:

> The file should have the `.ico` extension.
> Limitation: Has effect on Windows only.

SVG paths are silently ignored on Windows — the OS title bar falls back to the Flet engine binary's own icon. Use `presentation.brand.icon_path()`, which returns the procedurally generated `tidyra-icon.ico`. The SVG (`logo_path()`) drives in-UI rendering only. Regenerate the ICO with `uv run python tools/build_icon.py` whenever the SVG palette or proportions change. Captured in [known-issues/fix-log-2026-09-02.md](../../known-issues/fix-log-2026-09-02.md).

## 5. Flet 0.86+ service-registration rule (do not regress)

`Service` subclasses (`FilePicker`, `UrlLauncher`, `Audio`, `Clipboard`, `Geolocator`, …) MUST be added to `page.services`, NOT `page.overlay`. The old pattern still runs but produces two distinct failures:

1. The service renders as a red "Unknown control" block.
2. Every method call times out with `RuntimeError: Timeout waiting for invoke method listener for <ServiceName>`.

The rule is documented as a [known issue](../known-issues/fix-log-2026-09-02.md). Do not undo it.

## 6. `TYPE_CHECKING` for circular view imports

Views import the controller only under `if TYPE_CHECKING:`. The view and the controller would otherwise form a circular import. See `home.py`, `preview.py`, `results.py` for the pattern.

## 7. One concern per file

A view file owns one screen. A component file owns one reusable control. If a view file exceeds ~300 lines, split it. The current split (home / preview / results + 4 components) is the floor, not the ceiling.

## 8. Theme follows system

`page.theme_mode = ft.ThemeMode.SYSTEM` is the default. Any custom colour must work in both light and dark modes. Test by toggling your OS theme; do not introduce a Tidyra-only theme switch without an ADR.

## 9. Brand-mark palette

The SVG in `resources/tidyra-logo.svg` uses `#0F766E` (folder body) and `#5EEAD4` (file cards). If you add a sibling mark or a monochrome variant, export it from the same SVG and reuse the same palette. If the palette must change, file an ADR.