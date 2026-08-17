"""Modelo de Lancamento (transacao) e seus tipos."""

from dataclasses import dataclass
from enum import Enum

from .funding import FundingSource


class TransactionType(str, Enum):
    """Os tres grupos de lancamento do app."""

    FIXED = "fixed"
    VARIABLE = "variable"
    INVESTMENT = "investment"

    @property
    def label(self) -> str:
        return {
            TransactionType.FIXED: "Despesas Fixas",
            TransactionType.VARIABLE: "Despesas Variáveis",
            TransactionType.INVESTMENT: "Investimentos",
        }[self]

    @property
    def singular(self) -> str:
        return {
            TransactionType.FIXED: "Fixa",
            TransactionType.VARIABLE: "Variável",
            TransactionType.INVESTMENT: "Investimento",
        }[self]

    @property
    def is_recurring(self) -> bool:
        return self in RECURRING_TYPES

    @property
    def accepts_benefits(self) -> bool:
        """Investimento so sai do salario; despesas podem usar VR/VA."""
        return self in (TransactionType.FIXED, TransactionType.VARIABLE)


#: Tipos que sobrevivem a virada do mes e sao copiados para a nova competencia.
#: Regra de negocio: variaveis zeram todo mes; fixas e investimentos se mantem
#: enquanto a serie estiver ativa (ver `series.end_month`).
RECURRING_TYPES: tuple[TransactionType, ...] = (
    TransactionType.FIXED,
    TransactionType.INVESTMENT,
)


@dataclass(slots=True)
class Transaction:
    """Um lancamento pertencente a uma competencia mensal ('YYYY-MM')."""

    id: int | None
    description: str
    amount: float
    category_id: int
    type: TransactionType
    month_ref: str

    #: De qual saldo o valor saiu: salario, VR ou VA.
    funding: FundingSource = FundingSource.SALARY
    #: Vinculo com a recorrencia. None para despesas variaveis.
    series_id: int | None = None
    #: Ultima competencia em que a serie se repete. None = sem data final.
    end_month: str | None = None

    # Preenchidos por JOIN no repositorio, para a View nao precisar consultar de novo.
    category_name: str = ""
    category_color: str = "#9E9E9E"

    @staticmethod
    def from_row(row) -> "Transaction":
        keys = row.keys()
        return Transaction(
            id=row["id"],
            description=row["description"],
            amount=row["amount"],
            category_id=row["category_id"],
            type=TransactionType(row["type"]),
            month_ref=row["month_ref"],
            funding=FundingSource(row["funding"]) if "funding" in keys else FundingSource.SALARY,
            series_id=row["series_id"] if "series_id" in keys else None,
            end_month=row["end_month"] if "end_month" in keys else None,
            category_name=row["category_name"] if "category_name" in keys else "",
            category_color=row["category_color"] if "category_color" in keys else "#9E9E9E",
        )
