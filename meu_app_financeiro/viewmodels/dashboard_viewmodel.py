"""ViewModel da Tela 1 (Dashboard)."""

from models import Category, Transaction, TransactionType
from utils import format_currency

from .app_state import AppState
from .observable import Observable

SECTION_ORDER = (TransactionType.FIXED, TransactionType.VARIABLE, TransactionType.INVESTMENT)


class DashboardViewModel(Observable):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.state.add_listener(self.notify)  # perfil mudou -> Tela 1 redesenha

    # ------------------------------------------------------------------ leitura
    @property
    def month_ref(self) -> str:
        return self.state.current_month

    @property
    def greeting(self) -> str:
        return f"Olá, {self.state.display_name}"

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
    def available_balance(self) -> float:
        return self.monthly_income - self.total_spent

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

    # ------------------------------------------------------------------ escrita
    def add_transaction(
        self,
        description: str,
        amount: float,
        category_id: int,
        type_: TransactionType,
    ) -> None:
        self.state.transactions.create(
            description.strip() or "Sem descrição",
            amount,
            category_id,
            type_,
            self.month_ref,
        )
        self.notify()

    def update_transaction(
        self, transaction_id: int, description: str, amount: float, category_id: int
    ) -> None:
        self.state.transactions.update(
            transaction_id, description.strip() or "Sem descrição", amount, category_id
        )
        self.notify()

    def delete_transaction(self, transaction_id: int) -> None:
        self.state.transactions.delete(transaction_id)
        self.notify()

    def create_category(self, name: str, color: str, type_: TransactionType) -> Category:
        return self.state.categories.create(name, color, type_)

    def dispose(self) -> None:
        self.state.remove_listener(self.notify)
