"""Linha de um lançamento, com cor da categoria e ações de editar/excluir."""

from collections.abc import Callable

import flet as ft

from models import Transaction
from utils import format_currency, month_short_label

from . import theme
from .balance_card import WALLET_COLORS


def transaction_tile(
    item: Transaction,
    on_edit: Callable[[Transaction], None],
    on_delete: Callable[[Transaction], None],
    read_only: bool = False,
) -> ft.Container:
    # Legenda da categoria; recorrentes com prazo mostram até quando repetem.
    legenda: list[ft.Control] = [
        theme.color_dot(item.category_color, 8),
        ft.Text(item.category_name, size=11, color=theme.TEXT_MUTED),
    ]
    if item.funding.is_benefit:
        cor = WALLET_COLORS.get(item.funding.value, theme.PRIMARY)
        legenda.append(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=6, vertical=1),
                border_radius=6,
                bgcolor=cor,
                content=ft.Text(
                    item.funding.label,
                    size=10,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_700,
                ),
            )
        )
    if item.end_month:
        legenda.append(
            ft.Container(
                padding=ft.padding.symmetric(horizontal=6, vertical=1),
                border_radius=6,
                bgcolor="#1A104535",
                content=ft.Text(
                    f"até {month_short_label(item.end_month)}",
                    size=10,
                    color=theme.PRIMARY,
                    weight=ft.FontWeight.W_600,
                ),
            )
        )

    acoes: list[ft.Control] = (
        []
        if read_only
        else [
            ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,
                icon_size=18,
                icon_color=theme.TEXT_MUTED,
                tooltip="Editar",
                on_click=lambda _: on_edit(item),
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_size=18,
                icon_color=theme.DANGER,
                tooltip="Excluir",
                on_click=lambda _: on_delete(item),
            ),
        ]
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=theme.RADIUS_SM,
        bgcolor=theme.SURFACE,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Faixa vertical com a cor da categoria
                ft.Container(width=4, height=34, bgcolor=item.category_color, border_radius=4),
                ft.Column(
                    spacing=1,
                    expand=True,
                    controls=[
                        ft.Text(
                            item.description,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=theme.TEXT,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row(spacing=6, wrap=True, controls=legenda),
                    ],
                ),
                ft.Text(
                    format_currency(item.amount),
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=theme.TEXT,
                ),
                *acoes,
            ],
        ),
    )
