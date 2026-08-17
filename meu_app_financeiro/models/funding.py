"""Fontes de recurso: de qual saldo o lancamento foi pago."""

from enum import Enum


class FundingSource(str, Enum):
    """Carteiras do usuario.

    O salario paga qualquer coisa. VR e VA sao beneficios de uso restrito:
    so cobrem despesas fixas e variaveis de categorias marcadas como
    alimentacao (`Category.meal_eligible`).
    """

    SALARY = "salary"
    VR = "vr"
    VA = "va"

    @property
    def label(self) -> str:
        return {
            FundingSource.SALARY: "Salário",
            FundingSource.VR: "VR",
            FundingSource.VA: "VA",
        }[self]

    @property
    def long_label(self) -> str:
        return {
            FundingSource.SALARY: "Salário",
            FundingSource.VR: "Vale Refeição",
            FundingSource.VA: "Vale Alimentação",
        }[self]

    @property
    def is_benefit(self) -> bool:
        return self is not FundingSource.SALARY


#: Beneficios, na ordem em que aparecem na interface.
BENEFITS: tuple[FundingSource, ...] = (FundingSource.VR, FundingSource.VA)
