"""Result view — the summary on the results screen.

Same layout rule as :mod:`plan_view`: a single outer scrollable
Column owns the scroll context. Failure cards are direct children of
that Column so they scroll together with the rest of the result
summary — no nested scrolls.
"""

from __future__ import annotations

import flet as ft

from tidyra.domain.plans import FileOperation, OrganizationResult, SkipReason


def result_view(result: OrganizationResult) -> ft.Control:
    moved = len(result.succeeded) - len(result.failures)
    failed = len(result.failures)
    skipped = len(result.plan.skipped())

    summary = ft.Container(
        content=ft.Row(
            controls=[
                ft.Chip(label=ft.Text(f"{moved} moved"), bgcolor=ft.Colors.GREEN_100),
                *(
                    [
                        ft.Chip(
                            label=ft.Text(f"{failed} failed"),
                            bgcolor=ft.Colors.RED_100,
                        ),
                    ]
                    if failed
                    else []
                ),
                ft.Chip(label=ft.Text(f"{skipped} skipped"), bgcolor=ft.Colors.GREY_200),
            ],
            spacing=8,
        ),
        padding=ft.Padding.symmetric(vertical=8),
    )

    sections: list[ft.Control] = [
        summary,
        ft.Text(
            "Done. The same files you saw in the preview have been moved.",
            italic=True,
            color=ft.Colors.GREY,
        ),
    ]

    if failed:
        sections.append(ft.Text("Failures", weight=ft.FontWeight.BOLD))
        sections.extend(_failure_card(op, exc) for op, exc in result.failures)

    return ft.Column(
        controls=sections,
        spacing=12,
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
    )


def _failure_card(op: FileOperation, exc: Exception) -> ft.Control:
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(op.source.name, weight=ft.FontWeight.BOLD),
                    ft.Text(str(exc), color=ft.Colors.RED, size=11),
                ],
                spacing=2,
            ),
            padding=10,
        )
    )


def _skip_label(reason: SkipReason | None) -> str:
    if reason is None:
        return ""
    return reason.name.replace("_", " ").title()


__all__ = ["result_view"]
