"""Results view — done summary + back action."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from tidyra.presentation.components.result_view import result_view

if TYPE_CHECKING:
    from tidyra.presentation.controller import TidyraApp


def results_view(app: TidyraApp) -> ft.Control:
    state = app.state
    if state.result is None:
        return ft.Container(
            content=ft.Text("No result to display.", italic=True),
            padding=16,
        )

    header = ft.Container(
        content=ft.Text("Done", size=24, weight=ft.FontWeight.BOLD),
        padding=ft.Padding.symmetric(vertical=8),
    )

    actions = ft.Row(
        controls=[
            ft.ElevatedButton(
                "Organize another folder",
                icon=ft.Icons.RESTART_ALT,
                on_click=lambda _e: app.back_home(),
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    return ft.Container(
        content=ft.Column(
            controls=[header, result_view(state.result), actions],
            spacing=12,
            expand=True,
        ),
        padding=16,
        expand=True,
    )
