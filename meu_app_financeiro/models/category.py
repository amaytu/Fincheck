"""Modelo de Categoria."""

from dataclasses import dataclass

from .transaction import TransactionType


@dataclass(slots=True)
class Category:
    """Categoria de lancamento, com cor propria usada em listas e graficos."""

    id: int | None
    name: str
    color: str  # HEX, ex: "#E57373"
    type: TransactionType
    #: Categoria de alimentacao: pode ser paga com VR ou VA.
    meal_eligible: bool = False

    @staticmethod
    def from_row(row) -> "Category":
        keys = row.keys()
        return Category(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            type=TransactionType(row["type"]),
            meal_eligible=bool(row["meal_eligible"]) if "meal_eligible" in keys else False,
        )
