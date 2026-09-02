"""Tidyra — Flet application entry point."""

from __future__ import annotations

import flet as ft

from tidyra.application.services import OrganizeService
from tidyra.infrastructure.filesystem import LocalFileSystem
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
    page.overlay.append(picker)
    app.picker = picker

    app.render()


def run() -> None:
    """Console-script entry point — wraps ``main`` with ``ft.run``."""
    ft.run(main)
