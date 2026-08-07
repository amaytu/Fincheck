"""Linha de categoria com barra de progresso proporcional — Tela 2."""

import flet as ft

from utils import format_currency

from . import theme


def category_bar(name: str, total: float, color: str, ratio: float) -> ft.Container:
    return ft.Container(
        padding=ft.padding.symmetric(vertical=8),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=8,
                            tight=True,
                            controls=[
                                theme.color_dot(color, 10),
                                ft.Text(name, size=13, color=theme.TEXT),
                            ],
                        ),
                        ft.Text(
                            format_currency(total),
                            size=13,
                            weight=ft.FontWeight.W_700,
                            color=theme.TEXT,
                        ),
                    ],
                ),
                ft.Container(
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.ProgressBar(
                        value=max(0.02, min(1.0, ratio)),
                        color=color,
                        bgcolor=theme.TRACK,
                        bar_height=8,
                    ),
                ),
            ],
        ),
    )


def breakdown_card(title: str, accent: str, rows: list[dict]) -> ft.Container:
    """Bloco 'Fixas / Variáveis / Investimentos' do detalhamento por categoria."""
    body: list[ft.Control] = [
        ft.Row(
            spacing=8,
            controls=[
                ft.Container(width=4, height=18, bgcolor=accent, border_radius=4),
                ft.Text(title, size=14, weight=ft.FontWeight.W_700, color=theme.TEXT),
            ],
        )
    ]

    if rows:
        body.extend(
            category_bar(r["name"], r["total"], r["color"], r["ratio"]) for r in rows
        )
    else:
        body.append(
            ft.Container(
                padding=ft.padding.symmetric(vertical=12),
                content=ft.Text(
                    "Sem lançamentos neste mês.",
                    size=12,
                    italic=True,
                    color=theme.TEXT_MUTED,
                ),
            )
        )

    return theme.card(ft.Column(spacing=2, controls=body))
