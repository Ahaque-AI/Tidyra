"""Tidyra brand assets — logo path resolution for Flet.

Single source of truth for where the brand mark is, regardless of how
Tidyra is launched (``uv run tidyra``, ``python -m tidyra``, a frozen
PyInstaller binary, etc.).

Why a helper, not a constant: ``importlib.resources`` is the supported
way to read packaged data and it returns a traversable that works for
both editable installs (``uv run``) and installed wheels. ``__file__``
relative paths break under frozen binaries.

Two assets ship today:

- ``tidyra-logo.svg`` — the brand source. Drives in-UI rendering at
  any size.
- ``tidyra-icon.ico`` — the raster export used by the OS window
  decoration. Required because Flet 0.86's ``page.window.icon``
  expects ``.ico`` on Windows (see
  ``docs/docs/known-issues/fix-log-2026-09-02.md``). The ICO is
  procedurally generated from the brand source by
  ``tools/build_icon.py``; regenerate whenever the SVG palette or
  proportions change.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

_PACKAGE = "tidyra.resources"
_LOGO_FILENAME = "tidyra-logo.svg"
_ICON_FILENAME = "tidyra-icon.ico"


def logo_path() -> Path:
    """Return an absolute filesystem path to the Tidyra logo SVG.

    Used for in-UI rendering (``ft.Image(src=...)``). Works under
    ``uv run``, ``python -m tidyra``, and frozen distributions.
    """
    return Path(str(files(_PACKAGE).joinpath(_LOGO_FILENAME)))


def icon_path() -> Path:
    """Return an absolute filesystem path to the Tidyra window ``.ico``.

    Used for ``page.window.icon``. Flet 0.86 on Windows ignores
    anything that is not a ``.ico`` file (see the Flet source for
    ``Window.icon`` and the docs site known-issues entry). The
    matching SVG is exposed via ``logo_path()`` for in-app rendering.
    """
    return Path(str(files(_PACKAGE).joinpath(_ICON_FILENAME)))


__all__ = ["icon_path", "logo_path"]
