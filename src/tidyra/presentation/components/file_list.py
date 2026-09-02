"""File list — the discovered entries on the home screen.

The list lives inside a bordered card with ``expand=True`` so it fills
the available vertical space; the inner Column has
``ft.ScrollMode.ALWAYS`` so the glassmorphism scrollbar is always
visible. Each row carries the rule that matched the file (or the skip
reason when the file will not be moved) so the user can see the
classification without leaving the home screen.

Layout note: the parent layout MUST own the scroll context — if a
grandparent Column also has ``scroll=...``, wheel events get
ambiguous and the list never scrolls. The :func:`home_view` function
deliberately leaves its outer Column un-scrollable and gives this
card ``expand=True`` instead.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import flet as ft

from tidyra.domain.models import FileEntry
from tidyra.domain.plans import FileOperation, SkipReason

# Visual constants. Kept module-level so the row layout stays consistent
# without re-instantiating them per call.
_BORDER = ft.Colors.with_opacity(0.25, ft.Colors.ON_SURFACE)
_BG = ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE)

# Icon + color per status. ``matched`` covers all rows that have a rule
# (including the catch-all "other"). Skipped rows use the specific skip
# reason so the user immediately sees why a file is being left alone.
_STATUS_VISUAL: dict[str, tuple[ft.IconData, ft.Colors]] = {
    "matched": (ft.Icons.CHECK_CIRCLE_OUTLINE, ft.Colors.GREEN_400),
    "unmatched": (ft.Icons.HELP_OUTLINE, ft.Colors.GREY_400),
    "symlink": (ft.Icons.LINK, ft.Colors.AMBER_400),
    "not_a_file": (ft.Icons.FOLDER, ft.Colors.GREY_400),
    "outside_root": (ft.Icons.BLOCK, ft.Colors.RED_400),
    "destination_exists": (ft.Icons.FOLDER_SPECIAL, ft.Colors.RED_400),
    "no_op": (ft.Icons.REMOVE_CIRCLE_OUTLINE, ft.Colors.GREY_400),
    "rule_conflict": (ft.Icons.WARNING_AMBER, ft.Colors.RED_400),
    "nested_destination": (ft.Icons.PLACE, ft.Colors.RED_400),
}


def _visual_for(reason: SkipReason | None) -> tuple[ft.IconData, ft.Colors]:
    """Pick the icon + color pair for a row based on its skip reason."""
    if reason is None:
        return _STATUS_VISUAL["matched"]
    return _STATUS_VISUAL.get(reason.value, _STATUS_VISUAL["unmatched"])


def file_list(
    entries: Iterable[FileEntry],
    operations: Iterable[FileOperation] = (),
) -> ft.Control:
    """Render an always-scrollable, expandable list of discovered files.

    Each row shows the file's name, its human-readable size, and either
    the rule that classified it (when ``operations`` contains the
    matching :class:`FileOperation`) or the reason it will be skipped.

    Args:
        entries: Files discovered by the latest scan.
        operations: The operations from the latest plan. Used to look up
            the matched rule name and skip reason for each entry. When
            empty (e.g. the user just picked a folder and hasn't scanned
            yet), rows render with a neutral indicator and no rule chip.
    """
    entries_list = list(entries)
    if not entries_list:
        return ft.Text("No files found.", italic=True)

    op_by_source: dict[Path, FileOperation] = {op.source: op for op in operations}
    rows: list[ft.Control] = [_row(entry, op_by_source.get(entry.path)) for entry in entries_list]

    return ft.Container(
        content=ft.Column(
            controls=rows,
            scroll=ft.ScrollMode.ALWAYS,
            spacing=0,
        ),
        border=ft.Border.all(1, _BORDER),
        border_radius=8,
        bgcolor=_BG,
        expand=True,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        padding=4,
    )


def _row(entry: FileEntry, op: FileOperation | None) -> ft.Control:
    """Render a single row for one file."""
    icon_name, icon_color = _visual_for(op.skip_reason if op else None)
    rule_label = _rule_label(op)

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon_name, size=16, color=icon_color),
                ft.Container(
                    content=ft.Text(entry.name, expand=False, no_wrap=False),
                    expand=True,
                    padding=ft.Padding.symmetric(horizontal=8),
                ),
                rule_label,
                ft.Container(width=12),
                ft.Text(
                    _human_size(entry.size),
                    color=ft.Colors.GREY,
                    size=12,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=ft.Padding.symmetric(vertical=6, horizontal=8),
    )


def _rule_label(op: FileOperation | None) -> ft.Control:
    """Return the chip that shows the matched rule (or skip reason)."""
    if op is None:
        return ft.Container(
            content=ft.Text("not classified", size=11, italic=True, color=ft.Colors.GREY),
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
        )
    if op.skip_reason is not None:
        return ft.Container(
            content=ft.Text(
                _skip_label(op.skip_reason),
                size=11,
                color=ft.Colors.RED_300,
            ),
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.RED_300)),
            border_radius=12,
        )
    return ft.Container(
        content=ft.Text(
            op.rule_name or "match",
            size=11,
            color=ft.Colors.GREEN_300,
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.GREEN_300)),
        border_radius=12,
    )


def _skip_label(reason: SkipReason) -> str:
    """Short human-readable label for a skip reason."""
    return reason.name.replace("_", " ").title()


def _human_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


__all__ = ["file_list"]
