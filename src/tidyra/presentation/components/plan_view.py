"""Plan view — the proposed organization for the preview screen.

Layout note: the outer Column is the SINGLE scrollable region for the
whole plan. Earlier versions wrapped each section (Will move / Will
skip) in its own inner scrollable Column, but that nests two scroll
contexts — wheel events get captured by the outer one and the inner
ones never receive them, so the inner scrollbar never moves.

Now the outer Column has ``expand=True, scroll=ft.ScrollMode.ALWAYS``
so it fills the available space and the glassmorphism scrollbar from
the page theme is always visible. Every move card and skip card is
laid out as a direct child of that outer Column, so the whole plan
scrolls together as one unit.
"""

from __future__ import annotations

import flet as ft

from tidyra.domain.plans import FileOperation, OrganizationPlan, SkipReason


def plan_view(plan: OrganizationPlan) -> ft.Control:
    """Render a plan summary with one card per operation.

    Sections are interleaved (summary chips, "Will move" header, every
    move card, "Will skip" header, every skip card) so the single
    outer scroll can carry the user through the entire preview.
    """
    moves = plan.to_execute()
    skips = plan.skipped()

    summary = ft.Container(
        content=ft.Row(
            controls=[
                ft.Chip(
                    label=ft.Text(f"{len(moves)} to move"),
                    bgcolor=ft.Colors.GREEN_100,
                ),
                ft.Chip(
                    label=ft.Text(f"{len(skips)} to skip"),
                    bgcolor=ft.Colors.GREY_200,
                ),
            ],
            spacing=8,
        ),
        padding=ft.Padding.symmetric(vertical=8),
    )

    sections: list[ft.Control] = [summary]

    sections.append(ft.Text("Will move", weight=ft.FontWeight.BOLD, size=14))
    if moves:
        sections.extend(move_card(op) for op in moves)
    else:
        sections.append(ft.Text("Nothing to move.", italic=True))

    if skips:
        sections.append(ft.Text("Will skip", weight=ft.FontWeight.BOLD, size=14))
        sections.extend(skip_card(op) for op in skips)

    return ft.Column(
        controls=sections,
        spacing=8,
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
    )


def move_card(op: FileOperation) -> ft.Control:
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(op.source.name, weight=ft.FontWeight.BOLD),
                            ft.Text("→", color=ft.Colors.GREY),
                            ft.Text(str(op.destination.parent.name)),
                            ft.Container(expand=True),
                            ft.Chip(label=ft.Text(op.rule_name or "?")),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Text(str(op.destination), size=11, color=ft.Colors.GREY),
                ],
                spacing=4,
            ),
            padding=10,
        )
    )


def skip_card(op: FileOperation) -> ft.Control:
    return ft.Card(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SKIP_NEXT, size=16, color=ft.Colors.AMBER),
                    ft.Text(op.source.name, expand=True),
                    ft.Chip(label=ft.Text(_skip_label(op.skip_reason))),
                ],
            ),
            padding=10,
        )
    )


def _skip_label(reason: SkipReason | None) -> str:
    if reason is None:
        return ""
    return reason.name.replace("_", " ").title()


__all__ = ["move_card", "plan_view", "skip_card"]
