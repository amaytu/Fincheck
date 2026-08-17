"""Tela 2 — Relatórios: gráfico macro e detalhamento por categoria."""

from collections.abc import Callable

import flet as ft

from models import TransactionType
from viewmodels import GROUP_COLORS, ReportsViewModel

from .components import breakdown_card, chart_legend, donut_chart, theme

SECTION_ORDER = (TransactionType.FIXED, TransactionType.VARIABLE, TransactionType.INVESTMENT)


class ReportsView:
    route = "/reports"

    def __init__(
        self,
        page: ft.Page,
        vm: ReportsViewModel,
        navigate: Callable[[str], None],
    ) -> None:
        self.page = page
        self.vm = vm
        self.navigate = navigate

        self.month_title = ft.Text(
            "", size=16, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE
        )

        header = ft.Container(
            padding=ft.padding.only(left=8, right=8, top=12, bottom=12),
            bgcolor=theme.PRIMARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Mês anterior",
                        on_click=lambda _: self.vm.go_previous_month(),
                    ),
                    ft.Container(width=150, alignment=ft.alignment.center, content=self.month_title),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Próximo mês",
                        on_click=lambda _: self.vm.go_next_month(),
                    ),
                ],
            ),
        )

        self.body = ft.Column(spacing=theme.GAP, scroll=ft.ScrollMode.AUTO, expand=True)

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
                selected_index=1,
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

        self.vm.add_listener(self.render)

    def render(self) -> None:
        self.month_title.value = self.vm.month_title
        groups = self.vm.group_totals()

        controls: list[ft.Control] = [
            theme.card(
                ft.Column(
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Distribuição do mês",
                            size=13,
                            weight=ft.FontWeight.W_700,
                            color=theme.TEXT_MUTED,
                        ),
                        donut_chart(groups, self.vm.total_label, "Total do mês"),
                        chart_legend(groups),
                    ],
                )
            ),
            ft.Text(
                "Detalhamento por categoria",
                size=13,
                weight=ft.FontWeight.W_700,
                color=theme.TEXT_MUTED,
            ),
        ]

        for type_ in SECTION_ORDER:
            controls.append(
                breakdown_card(
                    title=type_.label,
                    accent=GROUP_COLORS[type_],
                    rows=self.vm.breakdown_of(type_),
                )
            )

        controls.append(ft.Container(height=12))
        self.body.controls = controls
        self.page.update()

    def _on_nav_change(self, e: ft.ControlEvent) -> None:
        index = e.control.selected_index
        if index == 0:
            self.navigate("/")
        elif index == 2:
            self.navigate("/profile")
        e.control.selected_index = 1
