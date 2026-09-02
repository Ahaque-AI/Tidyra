"""Entry point for ``python -m tidyra``.

Initialises structured logging before launching the Flet desktop window
so early startup errors still land in the configured sinks.
"""

from __future__ import annotations

import flet as ft

from tidyra.infrastructure.logging import configure_logging
from tidyra.presentation.app import main

if __name__ == "__main__":
    configure_logging()
    ft.run(main)
