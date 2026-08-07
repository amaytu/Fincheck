"""ViewModel da Tela 3 (Perfil)."""

from utils import parse_currency

from .app_state import AppState
from .observable import Observable


class ProfileViewModel(Observable):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

    @property
    def display_name(self) -> str:
        return self.state.profile.display_name

    @property
    def monthly_income(self) -> float:
        return self.state.profile.monthly_income

    @property
    def income_text(self) -> str:
        """Valor formatado para preencher o input (sem o simbolo R$)."""
        return f"{self.monthly_income:.2f}".replace(".", ",")

    def validate(self, name: str, income_text: str) -> str | None:
        """Retorna a mensagem de erro, ou None se estiver tudo certo."""
        if not name.strip():
            return "Informe como voce quer ser chamado."
        if parse_currency(income_text) <= 0:
            return "Informe uma renda mensal maior que zero."
        return None

    def save(self, name: str, income_text: str) -> None:
        """Persiste e notifica o AppState (a Tela 1 se atualiza sozinha)."""
        self.state.update_profile(name.strip(), parse_currency(income_text))
