"""Tela 1 — Dashboard: resumo do mês e lançamentos."""

from collections.abc import Callable

import flet as ft

from models import Transaction, TransactionType
from utils import format_currency, month_label
from viewmodels import DashboardViewModel

from .components import TransactionSheet, balance_card, section_panel, theme, transaction_tile

SECTION_ORDER = (TransactionType.FIXED, TransactionType.VARIABLE, TransactionType.INVESTMENT)


class DashboardView:
    route = "/"

    def __init__(
        self,
        page: ft.Page,
        vm: DashboardViewModel,
        navigate: Callable[[str], None],
    ) -> None:
        self.page = page
        self.vm = vm
        self.navigate = navigate

        # --- cabeçalho ------------------------------------------------------
        self.greeting_text = ft.Text(
            "", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE
        )
        self.income_text = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)

        header = ft.Container(
            padding=ft.padding.only(left=16, right=16, top=14, bottom=14),
            bgcolor=theme.PRIMARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Canto superior esquerdo -> Tela 3
                    ft.Container(
                        on_click=lambda _: self.navigate("/profile"),
                        border_radius=30,
                        ink=True,
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        content=ft.Row(spacing=6, tight=True, controls=[self.greeting_text]),
                        tooltip="Abrir meu perfil",
                    ),
                    # Canto superior direito (somente visualização)
                    ft.Column(
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text("Renda Mensal", size=10, color="#BFE0D6"),
                            self.income_text,
                        ],
                    ),
                ],
            ),
        )

        # --- corpo rolável --------------------------------------------------
        self.body = ft.Column(
            spacing=theme.GAP,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.view = ft.View(
            route=self.route,
            padding=0,
            bgcolor=theme.BACKGROUND,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    padding=ft.padding.only(
                        left=theme.PAGE_PADDING,
                        right=theme.PAGE_PADDING,
                        top=theme.PAGE_PADDING,
                        bottom=8,
                    ),
                    content=self.body,
                ),
            ],
            navigation_bar=ft.NavigationBar(
                selected_index=0,
                bgcolor=theme.SURFACE,
                indicator_color="#332FBF8F",
                on_change=self._on_nav_change,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Resumo"),
                    ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART_OUTLINE, label="Relatórios"),
                    ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, label="Perfil"),
                ],
            ),
        )

        self.sheet = TransactionSheet(
            page=page,
            list_categories=self.vm.categories_of,
            create_category=self.vm.create_category,
            on_submit=self._submit_transaction,
        )

        self.vm.add_listener(self.render)

    # ------------------------------------------------------------------ render
    def render(self) -> None:
        self.greeting_text.value = f"{self.vm.greeting} 👤"
        self.income_text.value = format_currency(self.vm.monthly_income)

        controls: list[ft.Control] = [
            balance_card(
                balance=self.vm.available_balance,
                income=self.vm.monthly_income,
                spent=self.vm.total_spent,
                month_title=month_label(self.vm.month_ref),
            ),
            ft.Container(height=2),
            ft.Text(
                "Lançamentos do mês",
                size=13,
                weight=ft.FontWeight.W_700,
                color=theme.TEXT_MUTED,
            ),
        ]

        for type_ in SECTION_ORDER:
            items = self.vm.items_of(type_)
            tiles = [
                transaction_tile(item, self._edit_transaction, self._confirm_delete)
                for item in items
            ]
            controls.append(
                section_panel(
                    type_=type_,
                    tiles=tiles,
                    total=self.vm.total_of(type_),
                    on_add=self._add_transaction,
                )
            )

        controls.append(ft.Container(height=12))
        self.body.controls = controls
        self.page.update()

    # ------------------------------------------------------------------ ações
    def _on_nav_change(self, e: ft.ControlEvent) -> None:
        index = e.control.selected_index
        if index == 1:
            self.navigate("/reports")
        elif index == 2:
            self.navigate("/profile")
        e.control.selected_index = 0  # o Dashboard segue sendo a aba base

    def _add_transaction(self, type_: TransactionType) -> None:
        self.sheet.open(type_)

    def _edit_transaction(self, item: Transaction) -> None:
        self.sheet.open(item.type, item)

    def _submit_transaction(
        self,
        transaction_id: int | None,
        description: str,
        amount: float,
        category_id: int,
        type_: TransactionType,
    ) -> None:
        if transaction_id is None:
            self.vm.add_transaction(description, amount, category_id, type_)
            message = "Lançamento adicionado."
        else:
            self.vm.update_transaction(transaction_id, description, amount, category_id)
            message = "Lançamento atualizado."
        self._toast(message)

    def _confirm_delete(self, item: Transaction) -> None:
        def do_delete(_: ft.ControlEvent) -> None:
            self.page.close(dialog)
            self.vm.delete_transaction(item.id)
            self._toast("Lançamento excluído.")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir lançamento"),
            content=ft.Text(f'Remover "{item.description}" deste mês?'),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.close(dialog)),
                ft.TextButton(
                    "Excluir",
                    on_click=do_delete,
                    style=ft.ButtonStyle(color=theme.DANGER),
                ),
            ],
        )
        self.page.open(dialog)

    def _toast(self, message: str) -> None:
        self.page.open(
            ft.SnackBar(content=ft.Text(message), bgcolor=theme.PRIMARY_DARK)
        )
