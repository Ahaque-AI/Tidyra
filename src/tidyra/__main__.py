"""Entry point for ``python -m tidyra``.

Uses Flet's ``run`` helper so the async main coroutine starts the
desktop window.
"""

from __future__ import annotations

import flet as ft

from tidyra.presentation.app import main

if __name__ == "__main__":
    ft.run(main)
