"""Tela 3 — Perfil e configurações."""

from collections.abc import Callable

import flet as ft

from viewmodels import ProfileViewModel

from .components import theme


class ProfileView:
    route = "/profile"

    def __init__(
        self,
        page: ft.Page,
        vm: ProfileViewModel,
        navigate: Callable[[str], None],
    ) -> None:
        self.page = page
        self.vm = vm
        self.navigate = navigate

        self.name_field = ft.TextField(
            label="Como você quer ser chamado?",
            hint_text="Ex.: Gabriel",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
            capitalization=ft.TextCapitalization.WORDS,
        )
        self.income_field = ft.TextField(
            label="Qual a sua renda mensal?",
            prefix_text="R$ ",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
        )
        self.error_text = ft.Text("", size=12, color=theme.DANGER, visible=False)

        header = ft.Container(
            padding=ft.padding.only(left=4, right=16, top=12, bottom=12),
            bgcolor=theme.PRIMARY,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Voltar",
                        on_click=lambda _: self.navigate("/"),
                    ),
                    ft.Text(
                        "Meu Perfil", size=17, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE
                    ),
                ],
            ),
        )

        form = theme.card(
            ft.Column(
                spacing=18,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=54,
                                height=54,
                                border_radius=27,
                                bgcolor="#1A1E6F5C",
                                alignment=ft.alignment.center,
                                content=ft.Icon(
                                    ft.Icons.ACCOUNT_CIRCLE, size=34, color=theme.PRIMARY
                                ),
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        "Dados pessoais",
                                        size=15,
                                        weight=ft.FontWeight.W_700,
                                        color=theme.TEXT,
                                    ),
                                    ft.Text(
                                        "Usados no cabeçalho e no cálculo do saldo.",
                                        size=11,
                                        color=theme.TEXT_MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=theme.DIVIDER),
                    self.name_field,
                    self.income_field,
                    self.error_text,
                ],
            )
        )

        footer = ft.Container(
            padding=ft.padding.only(left=16, right=16, top=8, bottom=20),
            bgcolor=theme.BACKGROUND,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=theme.TEXT_MUTED),
                            ft.Text(
                                "Alterar a renda mensal afetará o cálculo do mês atual e "
                                "dos próximos meses.",
                                size=11,
                                color=theme.TEXT_MUTED,
                                expand=True,
                            ),
                        ],
                    ),
                    ft.FilledButton(
                        text="Salvar Alterações",
                        icon=ft.Icons.SAVE_OUTLINED,
                        width=10_000,
                        height=52,
                        on_click=self._save,
                        style=ft.ButtonStyle(
                            bgcolor=theme.PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_SM),
                            text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_700),
                        ),
                    ),
                ],
            ),
        )

        self.view = ft.View(
            route=self.route,
            padding=0,
            bgcolor=theme.BACKGROUND,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    padding=ft.padding.all(theme.PAGE_PADDING),
                    content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[form]),
                ),
                footer,
            ],
        )

    def render(self) -> None:
        """Recarrega os campos com o que está persistido."""
        self.name_field.value = self.vm.display_name
        self.income_field.value = self.vm.income_text
        self.error_text.visible = False
        self.page.update()

    def _save(self, _: ft.ControlEvent) -> None:
        name = self.name_field.value or ""
        income = self.income_field.value or ""

        error = self.vm.validate(name, income)
        if error:
            self.error_text.value = error
            self.error_text.visible = True
            self.page.update()
            return

        self.vm.save(name, income)  # notifica o AppState -> Tela 1 já atualizada
        self.error_text.visible = False
        self.page.open(
            ft.SnackBar(content=ft.Text("Perfil atualizado."), bgcolor=theme.PRIMARY_DARK)
        )
        self.navigate("/")
