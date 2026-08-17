"""Tela 1 — Dashboard: resumo do mês e lançamentos."""

from collections.abc import Callable

import flet as ft

from models import FundingSource, Transaction, TransactionType
from utils import format_currency, month_label
from viewmodels import DashboardViewModel

from .components import (
    TransactionSheet,
    balance_card,
    section_panel,
    theme,
    transaction_tile,
    wallet_cards,
)

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

        self.month_text = ft.Text(
            "", size=13, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE
        )
        self.prev_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            tooltip="Mês anterior",
            on_click=lambda _: self.vm.go_previous_month(),
        )
        self.next_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            tooltip="Próximo mês",
            on_click=lambda _: self.vm.go_next_month(),
        )

        header = ft.Container(
            padding=ft.padding.only(left=16, right=16, top=14, bottom=6),
            bgcolor=theme.PRIMARY,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            # Canto superior esquerdo -> Tela 3
                            ft.Container(
                                on_click=lambda _: self.navigate("/profile"),
                                border_radius=30,
                                ink=True,
                                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                                content=ft.Row(
                                    spacing=6, tight=True, controls=[self.greeting_text]
                                ),
                                tooltip="Abrir meu perfil",
                            ),
                            # Canto superior direito (somente visualização)
                            ft.Column(
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text(
                                        "Renda Mensal", size=10, color=theme.ON_PRIMARY_MUTED
                                    ),
                                    self.income_text,
                                ],
                            ),
                        ],
                    ),
                    # Navegação de competência
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.prev_button,
                            ft.Container(
                                width=140,
                                alignment=ft.alignment.center,
                                content=self.month_text,
                            ),
                            self.next_button,
                        ],
                    ),
                ],
            ),
        )

        # Faixa de aviso exibida quando o mês visitado não é o corrente
        self.read_only_banner = ft.Container(
            visible=False,
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            border_radius=theme.RADIUS_SM,
            bgcolor="#1A104535",
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE, size=16, color=theme.PRIMARY),
                    ft.Text(
                        "Mês encerrado — somente leitura.",
                        size=12,
                        color=theme.PRIMARY,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                    ft.TextButton(
                        "Ir para o mês atual",
                        on_click=lambda _: self.vm.go_to_current_month(),
                        style=ft.ButtonStyle(color=theme.PRIMARY),
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
                indicator_color="#33CDAD56",
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
            funding_options=self.vm.funding_options,
            configured_benefits=self.vm.configured_benefits,
        )

        self.vm.add_listener(self.render)

    # ------------------------------------------------------------------ render
    def render(self) -> None:
        editable = self.vm.can_edit

        self.greeting_text.value = f"{self.vm.greeting} 👤"
        self.income_text.value = format_currency(self.vm.monthly_income)
        self.month_text.value = self.vm.month_title
        self.prev_button.disabled = not self.vm.can_go_previous
        self.next_button.disabled = not self.vm.can_go_next
        self.prev_button.icon_color = (
            ft.Colors.WHITE if self.vm.can_go_previous else theme.ON_PRIMARY_MUTED
        )
        self.next_button.icon_color = (
            ft.Colors.WHITE if self.vm.can_go_next else theme.ON_PRIMARY_MUTED
        )
        self.read_only_banner.visible = not editable

        controls: list[ft.Control] = []
        if not editable:
            controls.append(self.read_only_banner)

        controls.append(
            balance_card(
                balance=self.vm.available_balance,
                income=self.vm.monthly_income,
                spent=self.vm.salary_spent,
                month_title=month_label(self.vm.month_ref),
            )
        )

        carteiras = wallet_cards(self.vm.wallets())
        if carteiras is not None:
            controls.append(carteiras)

        if editable and not self.vm.is_configured:
            controls.append(self._setup_hint())

        controls.append(ft.Container(height=2))
        controls.append(
            ft.Text(
                "Lançamentos do mês",
                size=13,
                weight=ft.FontWeight.W_700,
                color=theme.TEXT_MUTED,
            )
        )

        for type_ in SECTION_ORDER:
            tiles = [
                transaction_tile(
                    item, self._edit_transaction, self._confirm_delete, read_only=not editable
                )
                for item in self.vm.items_of(type_)
            ]
            controls.append(
                section_panel(
                    type_=type_,
                    tiles=tiles,
                    total=self.vm.total_of(type_),
                    on_add=self._add_transaction,
                    read_only=not editable,
                )
            )

        controls.append(ft.Container(height=12))
        self.body.controls = controls
        self.page.update()

    def _setup_hint(self) -> ft.Container:
        """Primeiro uso: a renda ainda não foi definida."""
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            border_radius=theme.RADIUS_SM,
            bgcolor="#1ACDAD56",
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="#8A6D1F"),
                    ft.Text(
                        "Defina sua renda mensal no Perfil para o saldo fazer sentido.",
                        size=12,
                        color="#8A6D1F",
                        expand=True,
                    ),
                    ft.TextButton(
                        "Abrir",
                        on_click=lambda _: self.navigate("/profile"),
                        style=ft.ButtonStyle(color="#8A6D1F"),
                    ),
                ],
            ),
        )

    # ------------------------------------------------------------------ ações
    def _on_nav_change(self, e: ft.ControlEvent) -> None:
        index = e.control.selected_index
        if index == 1:
            self.navigate("/reports")
        elif index == 2:
            self.navigate("/profile")
        e.control.selected_index = 0  # o Dashboard segue sendo a aba base

    def _add_transaction(self, type_: TransactionType) -> None:
        self.sheet.open(type_, self.vm.month_ref)

    def _edit_transaction(self, item: Transaction) -> None:
        self.sheet.open(item.type, self.vm.month_ref, item)

    def _submit_transaction(
        self,
        transaction: Transaction | None,
        description: str,
        amount: float,
        category_id: int,
        type_: TransactionType,
        end_month: str | None,
        funding: FundingSource = FundingSource.SALARY,
    ) -> None:
        if transaction is None:
            self.vm.add_transaction(
                description, amount, category_id, type_, end_month, funding
            )
            message = "Lançamento adicionado."
        else:
            self.vm.update_transaction(
                transaction, description, amount, category_id, end_month, funding
            )
            message = (
                "Atualizado deste mês em diante."
                if transaction.series_id
                else "Lançamento atualizado."
            )
        self._toast(message)

    def _confirm_delete(self, item: Transaction) -> None:
        recorrente = item.series_id is not None

        def do_delete(_: ft.ControlEvent) -> None:
            self.page.close(dialog)
            self.vm.delete_transaction(item)
            self._toast(
                "Encerrado deste mês em diante." if recorrente else "Lançamento excluído."
            )

        if recorrente:
            texto = (
                f'"{item.description}" vai sumir deste mês e dos próximos. '
                "Os meses anteriores continuam como estão."
            )
        else:
            texto = f'Remover "{item.description}" deste mês?'

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Encerrar lançamento" if recorrente else "Excluir lançamento"),
            content=ft.Text(texto),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.close(dialog)),
                ft.TextButton(
                    "Encerrar" if recorrente else "Excluir",
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
