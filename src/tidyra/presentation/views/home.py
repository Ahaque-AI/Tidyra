"""Home view — folder selection + scan trigger."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from tidyra.presentation.components.file_list import file_list
from tidyra.presentation.components.folder_picker import folder_picker

if TYPE_CHECKING:
    from tidyra.presentation.controller import TidyraApp


def home_view(app: TidyraApp) -> ft.Control:
    state = app.state

    scan_button = ft.ElevatedButton(
        "Scan",
        icon=ft.Icons.SEARCH,
        on_click=lambda _e: app.scan(),
        disabled=state.root is None or state.loading,
    )

    contents: list[ft.Control] = [
        ft.Text("Tidyra", size=28, weight=ft.FontWeight.BOLD),
        ft.Text(
            "Pick a folder to organize. Tidyra will propose a plan before moving anything.",
            color=ft.Colors.GREY,
        ),
        folder_picker(path=str(state.root) if state.root else None, on_pick=app.pick_folder),
        ft.Divider(),
    ]

    if state.error:
        contents.append(
            ft.Container(
                content=ft.Text(state.error, color=ft.Colors.RED),
                padding=8,
            )
        )

    if state.entries:
        contents.append(
            ft.Text(
                f"Found {len(state.entries)} files",
                weight=ft.FontWeight.BOLD,
            )
        )
        contents.append(file_list(state.entries))

    contents.append(scan_button)

    if state.loading:
        contents.append(ft.ProgressRing())

    return ft.Container(
        content=ft.Column(controls=contents, spacing=16, scroll=ft.ScrollMode.AUTO),
        padding=16,
    )
