"""Seção expansível de lançamentos (Fixas / Variáveis / Investimentos)."""

from collections.abc import Callable

import flet as ft

from models import TransactionType
from utils import format_currency

from . import theme

SECTION_ICONS = {
    TransactionType.FIXED: ft.Icons.HOME_WORK_OUTLINED,
    TransactionType.VARIABLE: ft.Icons.SHOPPING_BAG_OUTLINED,
    TransactionType.INVESTMENT: ft.Icons.TRENDING_UP,
}

SECTION_COLORS = {
    TransactionType.FIXED: "#EF5350",
    TransactionType.VARIABLE: "#42A5F5",
    TransactionType.INVESTMENT: "#66BB6A",
}


def _tint(hex_color: str, alpha: str = "1A") -> str:
    """No Flet a cor com transparência é #AARRGGBB (alpha primeiro)."""
    return f"#{alpha}{hex_color.lstrip('#')}"


def section_panel(
    type_: TransactionType,
    tiles: list[ft.Control],
    total: float,
    on_add: Callable[[TransactionType], None],
    expanded: bool = True,
    read_only: bool = False,
) -> ft.Container:
    accent = SECTION_COLORS[type_]

    empty_hint = ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=14),
        content=ft.Text(
            "Nenhum lançamento neste mês.", size=12, color=theme.TEXT_MUTED, italic=True
        ),
    )

    add_button = ft.Container(
        padding=ft.padding.only(top=4, bottom=10, left=8, right=8),
        content=ft.Row(
            controls=[
                ft.OutlinedButton(
                    text=f"+ Adicionar {type_.singular}",
                    icon=ft.Icons.ADD,
                    expand=True,
                    on_click=lambda _: on_add(type_),
                    style=ft.ButtonStyle(
                        color=accent,
                        side=ft.BorderSide(1, accent),
                        shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=16, vertical=16),
                    ),
                )
            ]
        ),
    )

    return ft.Container(
        bgcolor=theme.SURFACE,
        border_radius=theme.RADIUS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        shadow=ft.BoxShadow(blur_radius=16, color="#0F000000", offset=ft.Offset(0, 4)),
        content=ft.ExpansionTile(
            initially_expanded=expanded,
            maintain_state=True,
            tile_padding=ft.padding.symmetric(horizontal=14, vertical=6),
            controls_padding=ft.padding.symmetric(horizontal=6),
            icon_color=theme.TEXT_MUTED,
            collapsed_icon_color=theme.TEXT_MUTED,
            text_color=theme.TEXT,
            collapsed_text_color=theme.TEXT,
            leading=ft.Container(
                width=38,
                height=38,
                border_radius=12,
                bgcolor=_tint(accent),
                alignment=ft.alignment.center,
                content=ft.Icon(SECTION_ICONS[type_], size=18, color=accent),
            ),
            title=ft.Text(type_.label, size=15, weight=ft.FontWeight.W_600),
            subtitle=ft.Row(
                spacing=6,
                controls=[
                    ft.Text(
                        format_currency(total),
                        size=13,
                        weight=ft.FontWeight.W_700,
                        color=accent,
                    ),
                    ft.Text("·", size=13, color=theme.TEXT_MUTED),
                    ft.Text(f"{len(tiles)} item(ns)", size=11, color=theme.TEXT_MUTED),
                ],
            ),
            controls=[*(tiles or [empty_hint]), *([] if read_only else [add_button])],
        ),
    )
