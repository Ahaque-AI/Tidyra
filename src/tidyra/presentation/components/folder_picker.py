"""Folder picker — the ``Select Folder`` row."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import flet as ft


def folder_picker(
    *,
    path: str | None,
    on_pick: Callable[[], Awaitable[None] | None],
) -> ft.Control:
    """Return a row showing the current path and a Select Folder button.

    ``on_pick`` may be sync or async; the event handler schedules the
    coroutine on the running loop so Flet awaits the result either way.
    """
    path_text = ft.Text(
        path if path else "No folder selected yet",
        selectable=True,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    def _dispatch(_event: object) -> None:
        result = on_pick()
        if asyncio.iscoroutine(result):
            asyncio.ensure_future(result)

    return ft.Row(
        controls=[
            ft.Container(content=path_text, expand=True, padding=8),
            ft.ElevatedButton(
                "Select Folder",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=_dispatch,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
