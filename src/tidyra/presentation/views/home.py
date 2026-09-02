"""Home view — folder selection + scan trigger.

Layout: the file list (when present) is the only scrollable region on
this screen. The outer Column has no scroll of its own — that was
causing wheel events to be captured by the page instead of the list,
so the list scrollbar never moved. With ``expand=True`` on the file
list card and ``expand=True`` on the root Container, the list fills
the available vertical space and the scan button stays pinned at the
bottom regardless of how many files were scanned.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from tidyra.presentation.brand import logo_path
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

    # Brand mark + wordmark. The logo is the same SVG used as the window
    # icon — see ``presentation/brand.py`` for the path resolver.
    brand_row = ft.Row(
        controls=[
            ft.Image(src=str(logo_path()), width=36, height=36, fit=ft.BoxFit.CONTAIN),
            ft.Text("Tidyra", size=28, weight=ft.FontWeight.BOLD),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Fixed-size content rendered above the file list.
    header: list[ft.Control] = [
        brand_row,
        ft.Text(
            "Pick a folder to organize. Tidyra will propose a plan before moving anything.",
            color=ft.Colors.GREY,
        ),
        folder_picker(path=str(state.root) if state.root else None, on_pick=app.pick_folder),
        ft.Container(
            content=ft.Row(
                controls=[
                    ft.Switch(
                        label="Recurse into subfolders",
                        value=state.recurse_subfolders,
                        on_change=lambda _e: app.toggle_recurse(),
                    ),
                    ft.Text(
                        "Walks every file under the chosen root and keeps the relative folder layout inside each rule destination.",
                        color=ft.Colors.GREY,
                        size=11,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=8),
        ),
        ft.Divider(),
    ]

    if state.error:
        header.append(
            ft.Container(
                content=ft.Text(state.error, color=ft.Colors.RED),
                padding=8,
            )
        )

    # Inner card that fills the available vertical space and owns the
    # scroll. ``expand=True`` so it grows/shrinks with the window.
    file_list_card: ft.Control | None = None
    if state.entries:
        header.append(
            ft.Text(
                f"Found {len(state.entries)} files",
                weight=ft.FontWeight.BOLD,
            )
        )
        operations = state.plan.operations if state.plan is not None else ()
        file_list_card = file_list(state.entries, operations)

    footer: list[ft.Control] = [scan_button]
    if state.loading:
        footer.append(ft.ProgressRing())

    controls: list[ft.Control] = list(header)
    if file_list_card is not None:
        controls.append(ft.Container(content=file_list_card, expand=True))
    controls.extend(footer)

    return ft.Container(
        content=ft.Column(controls=controls, spacing=16, expand=True),
        padding=16,
        expand=True,
    )
