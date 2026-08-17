"""ViewModel da Tela 1 (Dashboard)."""

from models import BENEFITS, Category, FundingSource, Transaction, TransactionType
from utils import format_currency, month_label, shift_month

from .app_state import AppState
from .observable import Observable

SECTION_ORDER = (TransactionType.FIXED, TransactionType.VARIABLE, TransactionType.INVESTMENT)


class DashboardViewModel(Observable):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.month_ref = state.current_month
        self.state.add_listener(self.notify)  # perfil mudou -> Tela 1 redesenha

    # ------------------------------------------------------------- navegacao
    @property
    def month_title(self) -> str:
        return month_label(self.month_ref)

    @property
    def is_current_month(self) -> bool:
        return self.month_ref == self.state.current_month

    @property
    def can_edit(self) -> bool:
        """Só o mês corrente aceita edição; o histórico é somente leitura."""
        return self.is_current_month

    @property
    def can_go_previous(self) -> bool:
        return self.month_ref > self.state.earliest_month()

    @property
    def can_go_next(self) -> bool:
        return self.month_ref < self.state.current_month

    def go_previous_month(self) -> None:
        if self.can_go_previous:
            self.month_ref = shift_month(self.month_ref, -1)
            self.notify()

    def go_next_month(self) -> None:
        if self.can_go_next:
            self.month_ref = shift_month(self.month_ref, 1)
            self.notify()

    def go_to_current_month(self) -> None:
        self.month_ref = self.state.current_month
        self.notify()

    # --------------------------------------------------------------- leitura
    @property
    def greeting(self) -> str:
        return f"Olá, {self.state.display_name}"

    @property
    def is_configured(self) -> bool:
        return self.state.is_configured

    @property
    def monthly_income(self) -> float:
        return self.state.income_of(self.month_ref)

    @property
    def income_label(self) -> str:
        return f"Renda Mensal: {format_currency(self.monthly_income)}"

    @property
    def total_spent(self) -> float:
        """Soma de todos os lancamentos do mes (fixas + variaveis + investimentos)."""
        return self.state.transactions.total_of_month(self.month_ref)

    @property
    def salary_spent(self) -> float:
        """Só o que saiu do salário. VR e VA têm saldo próprio."""
        return self.state.transactions.total_by_funding(self.month_ref, FundingSource.SALARY)

    @property
    def available_balance(self) -> float:
        return self.monthly_income - self.salary_spent

    def wallets(self) -> list[dict]:
        """Saldo de VR e VA. Só entram na tela as carteiras com valor definido."""
        carteiras = []
        for source in BENEFITS:
            total = self.state.amount_of(self.month_ref, source)
            if total <= 0:
                continue
            gasto = self.state.transactions.total_by_funding(self.month_ref, source)
            carteiras.append(
                {
                    "source": source,
                    "label": source.long_label,
                    "short": source.label,
                    "total": total,
                    "spent": gasto,
                    "balance": total - gasto,
                }
            )
        return carteiras

    def configured_benefits(self) -> list[FundingSource]:
        """VR e/ou VA com valor definido para o mês."""
        return [s for s in BENEFITS if self.state.amount_of(self.month_ref, s) > 0]

    def funding_options(self, category_id: int | None, type_: TransactionType) -> list[FundingSource]:
        """Carteiras que podem pagar este lançamento.

        VR e VA só aparecem em despesas (fixas ou variáveis) de categorias
        marcadas como alimentação, e só se o benefício estiver configurado.
        """
        opcoes = [FundingSource.SALARY]
        if not type_.accepts_benefits or category_id is None:
            return opcoes

        categoria = self.state.categories.get(category_id)
        if categoria is None or not categoria.meal_eligible:
            return opcoes

        opcoes.extend(
            s for s in BENEFITS if self.state.amount_of(self.month_ref, s) > 0
        )
        return opcoes

    @property
    def balance_label(self) -> str:
        return format_currency(self.available_balance)

    @property
    def is_negative(self) -> bool:
        return self.available_balance < 0

    def total_of(self, type_: TransactionType) -> float:
        return self.state.transactions.total_by_type(self.month_ref, type_)

    def items_of(self, type_: TransactionType) -> list[Transaction]:
        return self.state.transactions.list_by_month(self.month_ref, type_)

    def categories_of(self, type_: TransactionType) -> list[Category]:
        return self.state.categories.list_by_type(type_)

    # --------------------------------------------------------------- escrita
    def add_transaction(
        self,
        description: str,
        amount: float,
        category_id: int,
        type_: TransactionType,
        end_month: str | None = None,
        funding: FundingSource = FundingSource.SALARY,
    ) -> None:
        """Cria o lançamento. Recorrentes ganham uma série com vigência própria."""
        if not self.can_edit:
            return

        funding = self._validate_funding(funding, category_id, type_)
        series_id = None
        if type_.is_recurring:
            series_id = self.state.series.create(type_, self.month_ref, end_month)

        self.state.transactions.create(
            description.strip() or "Sem descrição",
            amount,
            category_id,
            type_,
            self.month_ref,
            series_id,
            funding,
        )
        if series_id is not None:
            # Preenche meses futuros que já tenham sido abertos.
            self.state.series.sync(series_id)
        self.notify()

    def update_transaction(
        self,
        item: Transaction,
        description: str,
        amount: float,
        category_id: int,
        end_month: str | None = None,
        funding: FundingSource = FundingSource.SALARY,
    ) -> None:
        """Edita o lançamento. Em recorrentes, vale deste mês em diante."""
        if not self.can_edit:
            return

        description = description.strip() or "Sem descrição"
        funding = self._validate_funding(funding, category_id, item.type)
        if item.series_id is None:
            self.state.transactions.update(
                item.id, description, amount, category_id, funding
            )
        else:
            self.state.transactions.update_series_forward(
                item.series_id, self.month_ref, description, amount, category_id, funding
            )
            self.state.series.set_end(item.series_id, end_month)
        self.notify()

    def _validate_funding(
        self,
        funding: FundingSource,
        category_id: int,
        type_: TransactionType,
    ) -> FundingSource:
        """Impede VR/VA fora do que a regra permite, mesmo se a UI deixar passar."""
        if funding in self.funding_options(category_id, type_):
            return funding
        return FundingSource.SALARY

    def delete_transaction(self, item: Transaction) -> None:
        """Exclui o lançamento.

        Variáveis somem apenas do mês. Recorrentes encerram a série a partir
        deste mês: some daqui em diante e o histórico fica intacto.
        """
        if not self.can_edit:
            return

        if item.series_id is None:
            self.state.transactions.delete(item.id)
        else:
            self.state.series.end_before(item.series_id, self.month_ref)
        self.notify()

    def create_category(
        self,
        name: str,
        color: str,
        type_: TransactionType,
        meal_eligible: bool = False,
    ) -> Category:
        return self.state.categories.create(name, color, type_, meal_eligible)

    def dispose(self) -> None:
        self.state.remove_listener(self.notify)
