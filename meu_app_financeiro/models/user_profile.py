"""Modelo de Perfil do usuario."""

from dataclasses import dataclass


@dataclass(slots=True)
class UserProfile:
    """Dados da Tela 3. A renda aqui e o padrao herdado por novos meses."""

    display_name: str = "Visitante"
    monthly_income: float = 0.0

    @staticmethod
    def from_row(row) -> "UserProfile":
        return UserProfile(
            display_name=row["display_name"],
            monthly_income=row["monthly_income"],
        )
