"""Result view — the summary on the results screen."""

from __future__ import annotations

import flet as ft

from tidyra.domain.plans import OrganizationResult, SkipReason


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

    failure_cards: list[ft.Control] = [
        ft.Card(
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
        for op, exc in result.failures
    ]

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
        sections.extend(failure_cards)

    return ft.Column(controls=sections, spacing=12)


def _skip_label(reason: SkipReason | None) -> str:
    if reason is None:
        return ""
    return reason.name.replace("_", " ").title()
