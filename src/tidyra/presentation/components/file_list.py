"""File list — the discovered entries on the home screen."""

from __future__ import annotations

from collections.abc import Sequence

import flet as ft

from tidyra.domain.models import FileEntry


def file_list(entries: Sequence[FileEntry]) -> ft.Control:
    """Render a compact, scrollable list of discovered files."""
    if not entries:
        return ft.Text("No files found.", italic=True)
    rows: list[ft.Control] = [
        ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.INSERT_DRIVE_FILE_OUTLINED,
                        size=16,
                        color=ft.Colors.GREY,
                    ),
                    ft.Text(entry.name, expand=True),
                    ft.Text(_human_size(entry.size), color=ft.Colors.GREY),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.symmetric(vertical=4),
        )
        for entry in entries
    ]
    return ft.Column(controls=rows, scroll=ft.ScrollMode.AUTO, spacing=0)


def _human_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"
