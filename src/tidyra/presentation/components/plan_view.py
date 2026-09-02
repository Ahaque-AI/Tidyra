"""Plan view — the proposed organization for the preview screen."""

from __future__ import annotations

import flet as ft

from tidyra.domain.plans import FileOperation, OrganizationPlan, SkipReason


def plan_view(plan: OrganizationPlan) -> ft.Control:
    """Render a plan summary with one card per executable operation."""
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

    move_cards: list[ft.Control] = (
        [move_card(op) for op in moves] if moves else [ft.Text("Nothing to move.", italic=True)]
    )
    skip_cards: list[ft.Control] = [skip_card(op) for op in skips] if skips else []

    sections: list[ft.Control] = [
        summary,
        ft.Text("Will move", weight=ft.FontWeight.BOLD, size=14),
        ft.Column(controls=move_cards, spacing=6, scroll=ft.ScrollMode.AUTO),
    ]
    if skip_cards:
        sections.append(ft.Text("Will skip", weight=ft.FontWeight.BOLD, size=14))
        sections.append(ft.Column(controls=skip_cards, spacing=6, scroll=ft.ScrollMode.AUTO))

    return ft.Column(controls=sections, spacing=12)


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
