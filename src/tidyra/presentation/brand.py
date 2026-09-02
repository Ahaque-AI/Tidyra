"""Tidyra brand assets — logo path resolution for Flet.

Single source of truth for where the brand mark is, regardless of how
Tidyra is launched (``uv run tidyra``, ``python -m tidyra``, a frozen
PyInstaller binary, etc.).

Why a helper, not a constant: ``importlib.resources`` is the supported
way to read packaged data and it returns a traversable that works for
both editable installs (``uv run``) and installed wheels. ``__file__``
relative paths break under frozen binaries.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

_PACKAGE = "tidyra.resources"
_LOGO_FILENAME = "tidyra-logo.svg"


def logo_path() -> Path:
    """Return an absolute filesystem path to the Tidyra logo SVG.

    Works under ``uv run``, ``python -m tidyra``, and frozen
    distributions. The returned path is what Flet's ``page.window.icon``
    and ``ft.Image(src=...)`` expect.
    """
    traversable = files(_PACKAGE).joinpath(_LOGO_FILENAME)
    # ``as_file`` returns a context manager; we want the path to outlive
    # the call, so resolve to a concrete Path up front. importlib caches
    # the underlying file handle internally — fine for our usage.
    return Path(str(traversable))


__all__ = ["logo_path"]
