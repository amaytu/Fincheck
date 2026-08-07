"""Camada de acesso a dados (Repository Pattern).

Os ViewModels conversam apenas com estas classes; nenhuma View executa SQL.
"""

import sqlite3

from models import RECURRING_TYPES, Category, Transaction, TransactionType, UserProfile

_TRANSACTION_SELECT = """
SELECT t.id, t.description, t.amount, t.category_id, t.type, t.month_ref,
       c.name AS category_name, c.color AS category_color
FROM transactions t
JOIN categories c ON c.id = t.category_id
"""


class ProfileRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get(self) -> UserProfile:
        row = self._conn.execute(
            "SELECT display_name, monthly_income FROM profile WHERE id = 1"
        ).fetchone()
        return UserProfile.from_row(row) if row else UserProfile()

    def save(self, display_name: str, monthly_income: float) -> None:
        self._conn.execute(
            "UPDATE profile SET display_name = ?, monthly_income = ? WHERE id = 1",
            (display_name, monthly_income),
        )
        self._conn.commit()


class CategoryRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list_by_type(self, type_: TransactionType) -> list[Category]:
        rows = self._conn.execute(
            "SELECT id, name, color, type FROM categories WHERE type = ? ORDER BY name",
            (type_.value,),
        ).fetchall()
        return [Category.from_row(r) for r in rows]

    def get(self, category_id: int) -> Category | None:
        row = self._conn.execute(
            "SELECT id, name, color, type FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        return Category.from_row(row) if row else None

    def create(self, name: str, color: str, type_: TransactionType) -> Category:
        """Cria a categoria ou devolve a existente de mesmo nome/tipo."""
        cursor = self._conn.execute(
            "INSERT OR IGNORE INTO categories (name, color, type) VALUES (?, ?, ?)",
            (name.strip(), color, type_.value),
        )
        self._conn.commit()
        if cursor.lastrowid:
            return Category(id=cursor.lastrowid, name=name.strip(), color=color, type=type_)
        row = self._conn.execute(
            "SELECT id, name, color, type FROM categories WHERE name = ? AND type = ?",
            (name.strip(), type_.value),
        ).fetchone()
        return Category.from_row(row)


class TransactionRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list_by_month(self, month_ref: str, type_: TransactionType) -> list[Transaction]:
        rows = self._conn.execute(
            _TRANSACTION_SELECT + "WHERE t.month_ref = ? AND t.type = ? ORDER BY t.id",
            (month_ref, type_.value),
        ).fetchall()
        return [Transaction.from_row(r) for r in rows]

    def create(
        self,
        description: str,
        amount: float,
        category_id: int,
        type_: TransactionType,
        month_ref: str,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO transactions (description, amount, category_id, type, month_ref)
               VALUES (?, ?, ?, ?, ?)""",
            (description, amount, category_id, type_.value, month_ref),
        )
        self._conn.commit()
        return cursor.lastrowid

    def update(self, transaction_id: int, description: str, amount: float, category_id: int) -> None:
        self._conn.execute(
            """UPDATE transactions
               SET description = ?, amount = ?, category_id = ?
               WHERE id = ?""",
            (description, amount, category_id, transaction_id),
        )
        self._conn.commit()

    def delete(self, transaction_id: int) -> None:
        self._conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self._conn.commit()

    def total_by_type(self, month_ref: str, type_: TransactionType) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions "
            "WHERE month_ref = ? AND type = ?",
            (month_ref, type_.value),
        ).fetchone()
        return float(row["total"])

    def total_of_month(self, month_ref: str) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE month_ref = ?",
            (month_ref,),
        ).fetchone()
        return float(row["total"])

    def totals_by_category(self, month_ref: str, type_: TransactionType) -> list[dict]:
        """Agregado usado na Tela 2: [{name, color, total}, ...] do maior ao menor."""
        rows = self._conn.execute(
            """SELECT c.name AS name, c.color AS color, SUM(t.amount) AS total
               FROM transactions t
               JOIN categories c ON c.id = t.category_id
               WHERE t.month_ref = ? AND t.type = ?
               GROUP BY c.id
               ORDER BY total DESC""",
            (month_ref, type_.value),
        ).fetchall()
        return [{"name": r["name"], "color": r["color"], "total": float(r["total"])} for r in rows]


class MonthRepository:
    """Responsavel pelo rollover de competencia e pela renda de cada mes."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def exists(self, month_ref: str) -> bool:
        return (
            self._conn.execute(
                "SELECT 1 FROM month_settings WHERE month_ref = ?", (month_ref,)
            ).fetchone()
            is not None
        )

    def income(self, month_ref: str) -> float:
        row = self._conn.execute(
            "SELECT income FROM month_settings WHERE month_ref = ?", (month_ref,)
        ).fetchone()
        if row:
            return float(row["income"])
        default = self._conn.execute(
            "SELECT monthly_income FROM profile WHERE id = 1"
        ).fetchone()
        return float(default["monthly_income"]) if default else 0.0

    def ensure_month(self, month_ref: str) -> None:
        """Abre a competencia se ela ainda nao existir (virada de mes).

        - Congela a renda vigente do perfil para o mes.
        - Copia os lancamentos recorrentes (fixas e investimentos) do ultimo
          mes existente. Variaveis nao sao copiadas: zeram na virada.
        """
        if self.exists(month_ref):
            return

        income_row = self._conn.execute(
            "SELECT monthly_income FROM profile WHERE id = 1"
        ).fetchone()
        income = float(income_row["monthly_income"]) if income_row else 0.0
        self._conn.execute(
            "INSERT INTO month_settings (month_ref, income) VALUES (?, ?)",
            (month_ref, income),
        )

        previous = self._conn.execute(
            "SELECT MAX(month_ref) AS m FROM month_settings WHERE month_ref < ?",
            (month_ref,),
        ).fetchone()
        if previous and previous["m"]:
            placeholders = ",".join("?" for _ in RECURRING_TYPES)
            self._conn.execute(
                f"""INSERT INTO transactions (description, amount, category_id, type, month_ref)
                    SELECT description, amount, category_id, type, ?
                    FROM transactions
                    WHERE month_ref = ? AND type IN ({placeholders})""",
                (month_ref, previous["m"], *[t.value for t in RECURRING_TYPES]),
            )
        self._conn.commit()

    def apply_income_from(self, month_ref: str, income: float) -> None:
        """Propaga a nova renda para o mes informado e todos os posteriores.

        Meses anteriores mantem o valor historico congelado.
        """
        self._conn.execute(
            "UPDATE month_settings SET income = ? WHERE month_ref >= ?",
            (income, month_ref),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO month_settings (month_ref, income) VALUES (?, ?)",
            (month_ref, income),
        )
        self._conn.commit()
