"""Linha de um lançamento, com cor da categoria e ações de editar/excluir."""

from collections.abc import Callable

import flet as ft

from models import Transaction
from utils import format_currency

from . import theme


def transaction_tile(
    item: Transaction,
    on_edit: Callable[[Transaction], None],
    on_delete: Callable[[Transaction], None],
) -> ft.Container:
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
                        ft.Row(
                            spacing=6,
                            controls=[
                                theme.color_dot(item.category_color, 8),
                                ft.Text(item.category_name, size=11, color=theme.TEXT_MUTED),
                            ],
                        ),
                    ],
                ),
                ft.Text(
                    format_currency(item.amount),
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=theme.TEXT,
                ),
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
            ],
        ),
    )
