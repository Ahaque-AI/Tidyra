"""Preview view — plan summary + confirm/back actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from tidyra.presentation.components.plan_view import plan_view

if TYPE_CHECKING:
    from tidyra.presentation.controller import TidyraApp


def preview_view(app: TidyraApp) -> ft.Control:
    state = app.state
    if state.plan is None:
        return ft.Container(
            content=ft.Text("No plan to display.", italic=True),
            padding=16,
        )

    moves = len(state.plan.to_execute())
    removals = len(state.plan.directory_removals)

    header = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Preview", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"Folder: {state.plan.root}",
                    color=ft.Colors.GREY,
                    size=11,
                ),
                ft.Text(
                    "Review the proposed moves below. Nothing happens until you press Organize.",
                    italic=True,
                    color=ft.Colors.GREY,
                ),
                *(
                    [
                        ft.Text(
                            f"{removals} folder(s) will be checked after organizing. Only folders still empty are removed.",
                            color=ft.Colors.AMBER,
                            size=11,
                        )
                    ]
                    if removals
                    else []
                ),
            ],
            spacing=4,
        ),
        padding=ft.Padding.symmetric(vertical=8),
    )

    actions = ft.Row(
        controls=[
            ft.OutlinedButton(
                "Back",
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _e: app.back_home(),
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Organize Files and Remove Empty Folders" if removals else "Organize Files",
                icon=ft.Icons.CHECK,
                on_click=lambda _e: app.organize(),
                disabled=(moves == 0 and removals == 0) or state.loading,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    body = ft.Container(
        content=plan_view(state.plan),
        expand=True,
    )

    return ft.Container(
        content=ft.Column(
            controls=[header, body, actions],
            spacing=12,
            expand=True,
        ),
        padding=16,
        expand=True,
    )
