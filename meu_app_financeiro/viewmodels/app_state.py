"""Estado global compartilhado entre as tres telas."""

import sqlite3

from database import (
    CategoryRepository,
    MonthRepository,
    ProfileRepository,
    TransactionRepository,
    init_db,
    mock_data,
)
from models import UserProfile
from utils import current_month_key

from .observable import Observable


class AppState(Observable):
    """Dono das dependencias (repositorios) e do perfil em memoria.

    Todos os ViewModels observam esta instancia, entao uma alteracao de perfil
    se propaga para o Dashboard e para os Relatorios sem reiniciar o app.
    """

    def __init__(self, conn: sqlite3.Connection, seed_mock: bool = True) -> None:
        super().__init__()
        self._conn = conn
        init_db(conn)

        self.profiles = ProfileRepository(conn)
        self.categories = CategoryRepository(conn)
        self.transactions = TransactionRepository(conn)
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

    def income_of(self, month_ref: str) -> float:
        return self.months.income(month_ref)

    def open_month(self, month_ref: str) -> None:
        """Garante que a competencia exista (usado ao navegar nos relatorios)."""
        self.months.ensure_month(month_ref)

    def update_profile(self, display_name: str, monthly_income: float) -> None:
        """Salva o perfil e propaga a renda do mes atual em diante."""
        self.profiles.save(display_name, monthly_income)
        self.months.apply_income_from(self.current_month, monthly_income)
        self._profile = self.profiles.get()
        self.notify()

    def refresh(self) -> None:
        """Forca o redesenho das telas observadoras."""
        self.notify()
