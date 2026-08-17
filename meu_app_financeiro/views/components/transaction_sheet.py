"""BottomSheet de criação/edição de lançamento (Tela 1).

Inclui o fluxo "Criar nova categoria" (nome + cor HEX) e, para lançamentos
recorrentes, o seletor "Repetir até" que define a vigência da série.
"""

from collections.abc import Callable

import flet as ft

from models import FundingSource, Transaction, TransactionType
from utils import month_options, parse_currency

from . import theme


class TransactionSheet:
    """Modal reutilizável. Instanciado uma vez por tela e reaberto sob demanda."""

    def __init__(
        self,
        page: ft.Page,
        list_categories: Callable[[TransactionType], list],
        create_category: Callable[..., object],
        on_submit: Callable[..., None],
        funding_options: Callable[..., list] | None = None,
        configured_benefits: Callable[[], list] | None = None,
    ) -> None:
        self.page = page
        self._list_categories = list_categories
        self._create_category = create_category
        self._on_submit = on_submit
        self._funding_options = funding_options or (lambda *_: [FundingSource.SALARY])
        self._configured_benefits = configured_benefits or (lambda: [])

        self._type: TransactionType = TransactionType.FIXED
        self._editing: Transaction | None = None
        self._month_ref: str = ""
        self._selected_color: str = theme.PRESET_COLORS[0]

        self.sheet = ft.BottomSheet(
            content=ft.Container(),
            is_scroll_controlled=True,
            enable_drag=True,
            show_drag_handle=True,
            maintain_bottom_view_insets_padding=True,
            bgcolor=theme.SURFACE,
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.only(top_left=24, top_right=24)),
        )

    # ------------------------------------------------------------------ público
    def open(
        self,
        type_: TransactionType,
        month_ref: str,
        transaction: Transaction | None = None,
    ) -> None:
        self._type = type_
        self._month_ref = month_ref
        self._editing = transaction
        self._selected_color = theme.PRESET_COLORS[0]
        self._build()
        self.page.open(self.sheet)

    def close(self) -> None:
        self.page.close(self.sheet)

    # ------------------------------------------------------------------ interno
    def _build(self) -> None:
        editing = self._editing
        categories = self._list_categories(self._type)

        self.description_field = ft.TextField(
            label="Descrição",
            value=editing.description if editing else "",
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
            capitalization=ft.TextCapitalization.SENTENCES,
        )
        self.amount_field = ft.TextField(
            label="Valor",
            prefix_text="R$ ",
            value=f"{editing.amount:.2f}".replace(".", ",") if editing else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
        )
        self.category_dropdown = ft.Dropdown(
            label="Categoria",
            value=str(editing.category_id) if editing else (str(categories[0].id) if categories else None),
            options=[ft.dropdown.Option(key=str(c.id), text=c.name) for c in categories],
            on_change=lambda _: self._refresh_funding(),
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
        )

        # --- de qual saldo sai (salário / VR / VA) ---------------------------
        self.funding_dropdown = ft.Dropdown(
            label="Pago com",
            value=(editing.funding.value if editing else FundingSource.SALARY.value),
            options=[],
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
        )
        self.funding_hint = ft.Text("", size=11, color=theme.TEXT_MUTED, visible=False)

        # --- vigência (só para fixas e investimentos) ------------------------
        self.recurrence_block = self._build_recurrence()

        # --- bloco "nova categoria" (oculto por padrão) -----------------------
        self.new_category_name = ft.TextField(
            label="Nome da nova categoria",
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
            capitalization=ft.TextCapitalization.SENTENCES,
        )
        self.new_category_hex = ft.TextField(
            label="Cor (HEX)",
            value=self._selected_color,
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.BACKGROUND,
            border_color=ft.Colors.TRANSPARENT,
            on_change=self._on_hex_typed,
        )
        self.swatches = ft.Row(wrap=True, spacing=8, run_spacing=8, controls=[])
        self._render_swatches()

        # Marca a categoria como alimentação, liberando pagamento com VR/VA.
        self.meal_switch = ft.Switch(
            label="É alimentação (aceita VR/VA)",
            value=False,
            active_color=theme.PRIMARY,
            visible=self._type.accepts_benefits,
            on_change=lambda _: self._refresh_funding(),
        )

        self.new_category_block = ft.Container(
            visible=False,
            padding=ft.padding.all(12),
            border_radius=theme.RADIUS_SM,
            bgcolor=theme.BACKGROUND,
            content=ft.Column(
                spacing=10,
                controls=[
                    self.new_category_name,
                    self.new_category_hex,
                    ft.Text("Cores sugeridas", size=11, color=theme.TEXT_MUTED),
                    self.swatches,
                    self.meal_switch,
                ],
            ),
        )

        self.toggle_new_category = ft.TextButton(
            text="+ Criar nova categoria",
            icon=ft.Icons.NEW_LABEL_OUTLINED,
            on_click=self._toggle_new_category,
            style=ft.ButtonStyle(color=theme.PRIMARY),
        )

        self.error_text = ft.Text("", size=12, color=theme.DANGER, visible=False)

        title = "Editar lançamento" if editing else f"Nova {self._type.singular}"

        controls: list[ft.Control] = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=theme.TEXT),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=theme.TEXT_MUTED,
                        on_click=lambda _: self.close(),
                    ),
                ],
            ),
            ft.Text(self._type.label, size=12, color=theme.TEXT_MUTED),
            self.description_field,
            self.amount_field,
            self.category_dropdown,
            self.toggle_new_category,
            self.new_category_block,
            self.funding_dropdown,
            self.funding_hint,
        ]
        if self.recurrence_block is not None:
            controls.append(self.recurrence_block)
        controls.append(self.error_text)
        controls.append(
            ft.Row(
                spacing=10,
                controls=[
                    ft.OutlinedButton(
                        text="Cancelar",
                        expand=True,
                        on_click=lambda _: self.close(),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(vertical=18),
                            shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_SM),
                        ),
                    ),
                    ft.FilledButton(
                        text="Salvar",
                        icon=ft.Icons.CHECK,
                        expand=True,
                        on_click=self._save,
                        style=ft.ButtonStyle(
                            bgcolor=theme.PRIMARY,
                            padding=ft.padding.symmetric(vertical=18),
                            shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_SM),
                        ),
                    ),
                ],
            )
        )

        self.sheet.content = ft.Container(
            padding=ft.padding.only(left=20, right=20, top=8, bottom=24),
            content=ft.Column(tight=True, spacing=14, scroll=ft.ScrollMode.AUTO, controls=controls),
        )
        self._refresh_funding(update=False)

    # ------------------------------------------------------------ carteiras
    def _allowed_funding(self) -> list[FundingSource]:
        """Carteiras válidas para a combinação atual de tipo e categoria."""
        if not self._type.accepts_benefits:
            return [FundingSource.SALARY]

        # Categoria nova ainda não existe no banco: decide pelo switch.
        if self.new_category_block.visible:
            if self.meal_switch.value:
                return [FundingSource.SALARY, *self._configured_benefits()]
            return [FundingSource.SALARY]

        category_id = (
            int(self.category_dropdown.value) if self.category_dropdown.value else None
        )
        return self._funding_options(category_id, self._type)

    def _refresh_funding(self, update: bool = True) -> None:
        permitidas = self._allowed_funding()
        self.funding_dropdown.options = [
            ft.dropdown.Option(key=s.value, text=s.long_label) for s in permitidas
        ]
        if self.funding_dropdown.value not in [s.value for s in permitidas]:
            self.funding_dropdown.value = FundingSource.SALARY.value

        so_salario = len(permitidas) == 1
        self.funding_dropdown.disabled = so_salario
        self.funding_hint.visible = so_salario and self._type.accepts_benefits
        self.funding_hint.value = (
            "VR e VA só pagam categorias de alimentação. Marque a categoria como "
            "alimentação e informe o benefício no Perfil."
            if so_salario
            else ""
        )
        if update:
            self.page.update()

    def _build_recurrence(self) -> ft.Control | None:
        """Seletor 'Repetir até'. Só existe para fixas e investimentos."""
        if not self._type.is_recurring:
            self.end_month_switch = None
            self.end_month_dropdown = None
            return None

        atual = self._editing.end_month if self._editing else None

        self.end_month_dropdown = ft.Dropdown(
            label="Repetir até",
            value=atual,
            options=[
                ft.dropdown.Option(key=key, text=label)
                for key, label in month_options(self._month_ref)
            ],
            visible=atual is not None,
            border_radius=theme.RADIUS_SM,
            filled=True,
            bgcolor=theme.SURFACE,
            border_color=ft.Colors.TRANSPARENT,
        )
        self.end_month_switch = ft.Switch(
            label="Definir data final",
            value=atual is not None,
            active_color=theme.PRIMARY,
            on_change=self._toggle_end_month,
        )

        return ft.Container(
            padding=ft.padding.all(12),
            border_radius=theme.RADIUS_SM,
            bgcolor=theme.BACKGROUND,
            content=ft.Column(
                spacing=8,
                controls=[
                    self.end_month_switch,
                    ft.Text(
                        "Sem data final, o lançamento se repete todo mês "
                        "indefinidamente.",
                        size=11,
                        color=theme.TEXT_MUTED,
                    ),
                    self.end_month_dropdown,
                ],
            ),
        )

    def _toggle_end_month(self, _: ft.ControlEvent) -> None:
        ligado = self.end_month_switch.value
        self.end_month_dropdown.visible = ligado
        if ligado and not self.end_month_dropdown.value:
            self.end_month_dropdown.value = self._month_ref
        self.page.update()

    def _render_swatches(self) -> None:
        self.swatches.controls = [
            ft.Container(
                width=30,
                height=30,
                bgcolor=color,
                border_radius=15,
                border=(
                    ft.border.all(3, theme.TEXT)
                    if color == self._selected_color
                    else ft.border.all(1, theme.DIVIDER)
                ),
                on_click=lambda _, c=color: self._pick_color(c),
            )
            for color in theme.PRESET_COLORS
        ]

    def _pick_color(self, color: str) -> None:
        self._selected_color = color
        self.new_category_hex.value = color
        self._render_swatches()
        self.page.update()

    def _on_hex_typed(self, _: ft.ControlEvent) -> None:
        self._selected_color = theme.normalize_hex(
            self.new_category_hex.value, self._selected_color
        )
        self._render_swatches()
        self.page.update()

    def _toggle_new_category(self, _: ft.ControlEvent) -> None:
        opened = not self.new_category_block.visible
        self.new_category_block.visible = opened
        self.category_dropdown.disabled = opened
        self.toggle_new_category.text = (
            "− Usar categoria existente" if opened else "+ Criar nova categoria"
        )
        self._refresh_funding()

    def _fail(self, message: str) -> None:
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()

    def _save(self, _: ft.ControlEvent) -> None:
        amount = parse_currency(self.amount_field.value)
        if amount <= 0:
            self._fail("Informe um valor maior que zero.")
            return

        end_month = None
        if self.end_month_switch is not None and self.end_month_switch.value:
            end_month = self.end_month_dropdown.value
            if not end_month:
                self._fail("Escolha até qual mês o lançamento se repete.")
                return

        if self.new_category_block.visible:
            name = (self.new_category_name.value or "").strip()
            if not name:
                self._fail("Dê um nome para a nova categoria.")
                return
            color = theme.normalize_hex(self.new_category_hex.value, self._selected_color)
            category = self._create_category(
                name, color, self._type, self.meal_switch.value
            )
            category_id = category.id
        else:
            if not self.category_dropdown.value:
                self._fail("Selecione ou crie uma categoria.")
                return
            category_id = int(self.category_dropdown.value)

        self._on_submit(
            transaction=self._editing,
            description=(self.description_field.value or "").strip(),
            amount=amount,
            category_id=category_id,
            type_=self._type,
            end_month=end_month,
            funding=FundingSource(self.funding_dropdown.value or "salary"),
        )
        self.close()
