"""Gráfico de rosca (donut) com o total do mês no centro — Tela 2."""

import flet as ft

from . import theme

CHART_SIZE = 230
RING_THICKNESS = 34


def donut_chart(groups: list[dict], center_value: str, center_label: str) -> ft.Container:
    """`groups` = [{'label', 'total', 'color', 'ratio'}, ...]."""
    visible = [g for g in groups if g["total"] > 0]

    if not visible:
        sections = [
            ft.PieChartSection(value=1, color=theme.TRACK, radius=RING_THICKNESS, title="")
        ]
    else:
        sections = [
            ft.PieChartSection(
                value=g["total"],
                color=g["color"],
                radius=RING_THICKNESS,
                title=f"{g['ratio'] * 100:.0f}%",
                title_style=ft.TextStyle(
                    size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
                ),
                title_position=0.5,
            )
            for g in visible
        ]

    chart = ft.PieChart(
        sections=sections,
        sections_space=2,
        center_space_radius=(CHART_SIZE / 2) - RING_THICKNESS - 6,
        start_degree_offset=270,
        width=CHART_SIZE,
        height=CHART_SIZE,
    )

    center = ft.Column(
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(center_label, size=11, color=theme.TEXT_MUTED),
            ft.Text(center_value, size=22, weight=ft.FontWeight.BOLD, color=theme.TEXT),
        ],
    )

    return ft.Container(
        alignment=ft.alignment.center,
        content=ft.Stack(
            width=CHART_SIZE,
            height=CHART_SIZE,
            controls=[
                chart,
                ft.Container(width=CHART_SIZE, height=CHART_SIZE, alignment=ft.alignment.center, content=center),
            ],
        ),
    )


def chart_legend(groups: list[dict]) -> ft.Row:
    """Legenda horizontal com a cor, o nome e o percentual de cada grupo."""
    return ft.Row(
        wrap=True,
        spacing=16,
        run_spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=6,
                tight=True,
                controls=[
                    theme.color_dot(g["color"], 10),
                    ft.Text(g["label"], size=12, color=theme.TEXT),
                    ft.Text(
                        f"{g['ratio'] * 100:.0f}%",
                        size=12,
                        weight=ft.FontWeight.W_700,
                        color=theme.TEXT_MUTED,
                    ),
                ],
            )
            for g in groups
        ],
    )
