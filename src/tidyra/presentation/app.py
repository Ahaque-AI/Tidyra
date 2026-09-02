"""Tidyra — Flet application entry point."""

from __future__ import annotations

import flet as ft

from tidyra.application.services import OrganizeService
from tidyra.infrastructure.filesystem import LocalFileSystem
from tidyra.infrastructure.logging import configure_logging, logger
from tidyra.presentation.controller import TidyraApp
from tidyra.presentation.state import UIState


async def main(page: ft.Page) -> None:
    """Flet async entry point. Invoked by ``uv run tidyra``."""
    page.title = "Tidyra"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.window.width = 760
    page.window.height = 640

    service = OrganizeService(LocalFileSystem())
    state = UIState(service=service)
    app = TidyraApp(page=page, state=state)
    state.on_navigate = app.render

    picker = ft.FilePicker()
    # Flet 0.86: services live on ``page.services``, not ``page.overlay``.
    # Adding a service to the overlay renders an "Unknown control" stub
    # and the client never wires up the invoke-method listener, which
    # causes every ``get_directory_path`` call to time out after 10 s.
    page.services.append(picker)
    app.picker = picker

    logger.bind(component="presentation", screen="home").info("tidyra app started")
    app.render()


def run() -> None:
    """Console-script entry point — wraps ``main`` with ``ft.run``.

    Initialises logging before Flet takes over so import-time failures
    (broken TOML, missing resources, etc.) still surface in the sinks.
    """
    configure_logging()
    ft.run(main)
