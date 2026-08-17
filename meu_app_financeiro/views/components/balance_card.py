"""Cards de saldo do mês (Tela 1): salário em destaque e os benefícios."""

import flet as ft

from utils import format_currency, safe_ratio

from . import theme

#: Cor de cada benefício, para diferenciar VR de VA na tela.
WALLET_COLORS = {"vr": "#7E57C2", "va": "#26A69A"}


def wallet_cards(wallets: list[dict]) -> ft.Control | None:
    """Linha com o saldo de VR e VA. None quando nenhum está configurado."""
    if not wallets:
        return None

    cartoes = []
    for w in wallets:
        cor = WALLET_COLORS.get(w["source"].value, theme.PRIMARY)
        estourou = w["balance"] < 0
        cartoes.append(
            ft.Container(
                expand=True,
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                border_radius=theme.RADIUS_SM,
                bgcolor=theme.SURFACE,
                border=ft.border.all(1, theme.DIVIDER),
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                theme.color_dot(cor, 8),
                                ft.Text(
                                    w["short"],
                                    size=11,
                                    weight=ft.FontWeight.W_700,
                                    color=cor,
                                ),
                                ft.Text(
                                    w["label"].split()[-1],
                                    size=9,
                                    color=theme.TEXT_MUTED,
                                    expand=True,
                                ),
                            ],
                        ),
                        ft.Text(
                            format_currency(w["balance"]),
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=theme.DANGER if estourou else theme.TEXT,
                        ),
                        ft.Container(
                            border_radius=6,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            content=ft.ProgressBar(
                                value=safe_ratio(w["spent"], w["total"]),
                                color=theme.DANGER if estourou else cor,
                                bgcolor=theme.TRACK,
                                bar_height=5,
                            ),
                        ),
                        ft.Text(
                            f"{format_currency(w['spent'])} de {format_currency(w['total'])}",
                            size=10,
                            color=theme.TEXT_MUTED,
                        ),
                    ],
                ),
            )
        )

    return ft.Row(spacing=theme.GAP, controls=cartoes)


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
                ft.Text(label, size=11, color=theme.ON_PRIMARY_MUTED),
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
        shadow=ft.BoxShadow(blur_radius=22, color="#33104535", offset=ft.Offset(0, 10)),
        content=ft.Column(
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Saldo Disponível", size=13, color=theme.ON_PRIMARY_MUTED),
                ft.Text(
                    format_currency(balance),
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=theme.GOLD if not negative else "#FFAB91",
                ),
                ft.Text(month_title, size=11, color=theme.ON_PRIMARY_MUTED),
                ft.Container(height=8),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    controls=[
                        mini("Salário", income, ft.Colors.WHITE),
                        ft.Container(width=1, height=28, bgcolor="#33FFFFFF"),
                        mini("Saiu do salário", spent, theme.GOLD_SOFT),
                    ],
                ),
            ],
        ),
    )
