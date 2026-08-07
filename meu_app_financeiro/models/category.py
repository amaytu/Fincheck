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

    @staticmethod
    def from_row(row) -> "Category":
        return Category(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            type=TransactionType(row["type"]),
        )
