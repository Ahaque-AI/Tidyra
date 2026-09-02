"""Flet build entry point — re-exports ``main`` for the packaged app.

The real async Flet entry lives in :mod:`tidyra.presentation.app` along
with all of the views and components. ``flet build`` packages the
whole ``src/tidyra`` tree (see ``tool.flet.app`` in ``pyproject.toml``)
and looks for an async ``main(page)`` coroutine at the module path
declared in ``tool.flet.app.module``.

This shim re-exports :func:`tidyra.presentation.app.main` so the build
can resolve the entry point at ``tidyra/main.py`` without forcing a
restructure of the package layout.

The console-script entry point in ``[project.scripts]`` keeps pointing
at ``tidyra.presentation.app:run`` (which calls ``configure_logging``
before ``ft.run(main)``) — that path is unchanged and unaffected by
this shim.
"""

from __future__ import annotations

from tidyra.presentation.app import main

__all__ = ["main"]
