"""Modelo de Perfil do usuario."""

from dataclasses import dataclass

from .funding import FundingSource


@dataclass(slots=True)
class UserProfile:
    """Dados da Tela 3. Os valores aqui sao o padrao herdado por novos meses."""

    display_name: str = "Visitante"
    monthly_income: float = 0.0
    vr_income: float = 0.0
    va_income: float = 0.0

    def amount_of(self, source: FundingSource) -> float:
        return {
            FundingSource.SALARY: self.monthly_income,
            FundingSource.VR: self.vr_income,
            FundingSource.VA: self.va_income,
        }[source]

    @staticmethod
    def from_row(row) -> "UserProfile":
        keys = row.keys()
        return UserProfile(
            display_name=row["display_name"],
            monthly_income=row["monthly_income"],
            vr_income=row["vr_income"] if "vr_income" in keys else 0.0,
            va_income=row["va_income"] if "va_income" in keys else 0.0,
        )
