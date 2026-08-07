"""Meu App Financeiro — ponto de entrada.

Arquitetura MVVM:
    models/       -> entidades puras (Transaction, Category, UserProfile)
    database/     -> SQLite + repositórios (única camada que executa SQL)
    viewmodels/   -> estado reativo e regras de apresentação
    views/        -> Flet (nenhuma regra de negócio aqui)
"""

import os

import flet as ft

from database import get_connection
from viewmodels import AppState, DashboardViewModel, ProfileViewModel, ReportsViewModel
from views import DashboardView, ProfileView, ReportsView
from views.components import theme

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def main(page: ft.Page) -> None:
    # --- configuração da janela / tema ---------------------------------------
    page.title = "Meu App Financeiro"
    page.theme = theme.app_theme()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = theme.BACKGROUND
    page.padding = 0
    page.window.width = 412       # proporção de um celular, para testar no desktop
    page.window.height = 880
    page.window.min_width = 360

    # --- composição das dependências (MVVM) ----------------------------------
    connection = get_connection()
    state = AppState(connection)

    dashboard_vm = DashboardViewModel(state)
    reports_vm = ReportsViewModel(state)
    profile_vm = ProfileViewModel(state)

    def navigate(route: str) -> None:
        page.go(route)

    dashboard = DashboardView(page, dashboard_vm, navigate)
    reports = ReportsView(page, reports_vm, navigate)
    profile = ProfileView(page, profile_vm, navigate)
    screens = {v.route: v for v in (dashboard, reports, profile)}

    # --- roteamento ----------------------------------------------------------
    def route_change(_: ft.RouteChangeEvent) -> None:
        target = screens.get(page.route, dashboard)

        page.views.clear()
        page.views.append(dashboard.view)          # Dashboard é sempre a base da pilha
        if target is not dashboard:
            page.views.append(target.view)

        dashboard.render()
        if target is not dashboard:
            target.render()
        page.update()

    def view_pop(_: ft.ViewPopEvent) -> None:
        """Botão físico "voltar" do Android."""
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    def on_disconnect(_) -> None:
        connection.close()

    page.on_disconnect = on_disconnect

    page.go(page.route or "/")


if __name__ == "__main__":
    ft.app(target=main, assets_dir=ASSETS_DIR, use_color_emoji=True)
