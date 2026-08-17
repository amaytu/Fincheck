"""Estado global compartilhado entre as tres telas."""

import sqlite3

from database import (
    CategoryRepository,
    MonthRepository,
    ProfileRepository,
    SeriesRepository,
    TransactionRepository,
    init_db,
    mock_data,
)
from models import FundingSource, UserProfile
from utils import current_month_key

from .observable import Observable


class AppState(Observable):
    """Dono das dependencias (repositorios) e do perfil em memoria.

    Todos os ViewModels observam esta instancia, entao uma alteracao de perfil
    se propaga para o Dashboard e para os Relatorios sem reiniciar o app.
    """

    def __init__(self, conn: sqlite3.Connection, seed_mock: bool = False) -> None:
        super().__init__()
        self._conn = conn
        init_db(conn)

        self.profiles = ProfileRepository(conn)
        self.categories = CategoryRepository(conn)
        self.transactions = TransactionRepository(conn)
        self.series = SeriesRepository(conn)
        self.months = MonthRepository(conn)

        if seed_mock:
            mock_data.seed(conn)

        self.current_month = current_month_key()
        self.months.ensure_month(self.current_month)  # aplica o rollover se preciso
        self._profile = self.profiles.get()

    @property
    def profile(self) -> UserProfile:
        return self._profile

    @property
    def display_name(self) -> str:
        return self._profile.display_name or "Visitante"

    @property
    def is_configured(self) -> bool:
        """False enquanto o usuario nao definiu renda no perfil."""
        return self._profile.monthly_income > 0

    def income_of(self, month_ref: str) -> float:
        return self.months.amount(month_ref, FundingSource.SALARY)

    def amount_of(self, month_ref: str, source: FundingSource) -> float:
        return self.months.amount(month_ref, source)

    def is_past(self, month_ref: str) -> bool:
        return month_ref < self.current_month

    def open_month(self, month_ref: str) -> None:
        """Materializa a competencia, exceto no passado.

        Meses anteriores ao atual nunca sao criados: o historico e somente
        leitura, entao abrir um mes antigo nao pode gerar lancamentos novos.
        """
        if self.is_past(month_ref):
            return
        self.months.ensure_month(month_ref)

    def earliest_month(self) -> str:
        """Primeira competencia com dados, usada para limitar a navegacao."""
        abertos = self.months.opened_months()
        return abertos[0] if abertos else self.current_month

    def update_profile(
        self,
        display_name: str,
        monthly_income: float,
        vr_income: float = 0.0,
        va_income: float = 0.0,
    ) -> None:
        """Salva o perfil e propaga as entradas do mes atual em diante."""
        self.profiles.save(display_name, monthly_income, vr_income, va_income)
        self.months.apply_incomes_from(
            self.current_month, monthly_income, vr_income, va_income
        )
        self._profile = self.profiles.get()
        self.notify()

    def refresh(self) -> None:
        """Forca o redesenho das telas observadoras."""
        self.notify()
