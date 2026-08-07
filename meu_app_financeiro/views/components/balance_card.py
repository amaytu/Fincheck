"""Card de destaque com o Saldo Disponível do mês (Tela 1)."""

import flet as ft

from utils import format_currency

from . import theme


def balance_card(
    balance: float,
    income: float,
    spent: float,
    month_title: str,
) -> ft.Container:
    negative = balance < 0

    def mini(label: str, value: float, color: str) -> ft.Column:
        return ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(label, size=11, color="#CFE6DF"),
                ft.Text(format_currency(value), size=13, weight=ft.FontWeight.W_600, color=color),
            ],
        )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=22),
        border_radius=theme.RADIUS + 4,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[theme.PRIMARY, theme.PRIMARY_DARK],
        ),
        shadow=ft.BoxShadow(blur_radius=22, color="#2A1E6F5C", offset=ft.Offset(0, 10)),
        content=ft.Column(
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Saldo Disponível", size=13, color="#CFE6DF"),
                ft.Text(
                    format_currency(balance),
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if not negative else "#FFCDD2",
                ),
                ft.Text(month_title, size=11, color="#A9CFC4"),
                ft.Container(height=8),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    controls=[
                        mini("Renda", income, ft.Colors.WHITE),
                        ft.Container(width=1, height=28, bgcolor="#33FFFFFF"),
                        mini("Lançamentos", spent, "#FFE0B2"),
                    ],
                ),
            ],
        ),
    )
