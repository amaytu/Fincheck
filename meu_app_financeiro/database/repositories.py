"""Camada de acesso a dados (Repository Pattern).

Os ViewModels conversam apenas com estas classes; nenhuma View executa SQL.
"""

import sqlite3

from models import (
    RECURRING_TYPES,
    Category,
    FundingSource,
    Transaction,
    TransactionType,
    UserProfile,
)
from utils import shift_month

_TRANSACTION_SELECT = """
SELECT t.id, t.description, t.amount, t.category_id, t.type, t.month_ref, t.series_id,
       t.funding,
       s.end_month AS end_month,
       c.name AS category_name, c.color AS category_color
FROM transactions t
JOIN categories c ON c.id = t.category_id
LEFT JOIN series s ON s.id = t.series_id
"""


class ProfileRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get(self) -> UserProfile:
        row = self._conn.execute(
            "SELECT display_name, monthly_income, vr_income, va_income "
            "FROM profile WHERE id = 1"
        ).fetchone()
        return UserProfile.from_row(row) if row else UserProfile()

    def save(
        self,
        display_name: str,
        monthly_income: float,
        vr_income: float = 0.0,
        va_income: float = 0.0,
    ) -> None:
        self._conn.execute(
            """UPDATE profile
               SET display_name = ?, monthly_income = ?, vr_income = ?, va_income = ?
               WHERE id = 1""",
            (display_name, monthly_income, vr_income, va_income),
        )
        self._conn.commit()


class CategoryRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list_by_type(self, type_: TransactionType) -> list[Category]:
        rows = self._conn.execute(
            "SELECT id, name, color, type, meal_eligible FROM categories "
            "WHERE type = ? ORDER BY name",
            (type_.value,),
        ).fetchall()
        return [Category.from_row(r) for r in rows]

    def get(self, category_id: int) -> Category | None:
        row = self._conn.execute(
            "SELECT id, name, color, type, meal_eligible FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
        return Category.from_row(row) if row else None

    def create(
        self,
        name: str,
        color: str,
        type_: TransactionType,
        meal_eligible: bool = False,
    ) -> Category:
        """Cria a categoria ou devolve a existente de mesmo nome/tipo."""
        cursor = self._conn.execute(
            "INSERT OR IGNORE INTO categories (name, color, type, meal_eligible) "
            "VALUES (?, ?, ?, ?)",
            (name.strip(), color, type_.value, int(meal_eligible)),
        )
        self._conn.commit()
        if cursor.lastrowid:
            return Category(
                id=cursor.lastrowid,
                name=name.strip(),
                color=color,
                type=type_,
                meal_eligible=meal_eligible,
            )
        row = self._conn.execute(
            "SELECT id, name, color, type, meal_eligible FROM categories "
            "WHERE name = ? AND type = ?",
            (name.strip(), type_.value),
        ).fetchone()
        return Category.from_row(row)

    def set_meal_eligible(self, category_id: int, meal_eligible: bool) -> None:
        self._conn.execute(
            "UPDATE categories SET meal_eligible = ? WHERE id = ?",
            (int(meal_eligible), category_id),
        )
        self._conn.commit()


class SeriesRepository:
    """Vigência dos lançamentos recorrentes (fixas e investimentos)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(self, type_: TransactionType, start_month: str, end_month: str | None) -> int:
        cursor = self._conn.execute(
            "INSERT INTO series (type, start_month, end_month) VALUES (?, ?, ?)",
            (type_.value, start_month, end_month),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get(self, series_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT id, type, start_month, end_month FROM series WHERE id = ?", (series_id,)
        ).fetchone()

    def set_end(self, series_id: int, end_month: str | None) -> None:
        """Redefine a data final e reconcilia as ocorrências já materializadas."""
        self._conn.execute(
            "UPDATE series SET end_month = ? WHERE id = ?", (end_month, series_id)
        )
        if end_month is not None:
            self._conn.execute(
                "DELETE FROM transactions WHERE series_id = ? AND month_ref > ?",
                (series_id, end_month),
            )
        self._conn.commit()
        self.sync(series_id)

    def end_before(self, series_id: int, from_month: str) -> None:
        """Encerra a série a partir de `from_month` (inclusive).

        Os meses anteriores permanecem intactos. Se não sobrar nenhuma
        ocorrência, a série inteira é removida.
        """
        last = shift_month(from_month, -1)
        self._conn.execute(
            "DELETE FROM transactions WHERE series_id = ? AND month_ref >= ?",
            (series_id, from_month),
        )
        row = self.get(series_id)
        if row and row["start_month"] > last:
            self._conn.execute("DELETE FROM series WHERE id = ?", (series_id,))
        else:
            self._conn.execute(
                "UPDATE series SET end_month = ? WHERE id = ?", (last, series_id)
            )
        self._conn.commit()

    def sync(self, series_id: int) -> None:
        """Replica a ocorrência nos meses já abertos que estão na vigência.

        Necessário em dois casos: quando o usuário estende a data final (os
        meses materializados no meio ficariam sem o lançamento) e quando cria
        um recorrente havendo meses futuros já abertos.
        """
        base = self._conn.execute(
            _TRANSACTION_SELECT + "WHERE t.series_id = ? ORDER BY t.month_ref DESC LIMIT 1",
            (series_id,),
        ).fetchone()
        if base is None:
            return

        row = self.get(series_id)
        end = row["end_month"] if row else None
        faltantes = self._conn.execute(
            """SELECT ms.month_ref FROM month_settings ms
               WHERE ms.month_ref > ?
                 AND (? IS NULL OR ms.month_ref <= ?)
                 AND NOT EXISTS (
                     SELECT 1 FROM transactions t
                     WHERE t.series_id = ? AND t.month_ref = ms.month_ref)
               ORDER BY ms.month_ref""",
            (base["month_ref"], end, end, series_id),
        ).fetchall()
        for f in faltantes:
            self._conn.execute(
                """INSERT INTO transactions
                       (description, amount, category_id, type, month_ref, series_id, funding)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    base["description"],
                    base["amount"],
                    base["category_id"],
                    base["type"],
                    f["month_ref"],
                    series_id,
                    base["funding"],
                ),
            )
        self._conn.commit()


class TransactionRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list_by_month(self, month_ref: str, type_: TransactionType) -> list[Transaction]:
        rows = self._conn.execute(
            _TRANSACTION_SELECT + "WHERE t.month_ref = ? AND t.type = ? ORDER BY t.id",
            (month_ref, type_.value),
        ).fetchall()
        return [Transaction.from_row(r) for r in rows]

    def get(self, transaction_id: int) -> Transaction | None:
        row = self._conn.execute(
            _TRANSACTION_SELECT + "WHERE t.id = ?", (transaction_id,)
        ).fetchone()
        return Transaction.from_row(row) if row else None

    def create(
        self,
        description: str,
        amount: float,
        category_id: int,
        type_: TransactionType,
        month_ref: str,
        series_id: int | None = None,
        funding: FundingSource = FundingSource.SALARY,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO transactions
                   (description, amount, category_id, type, month_ref, series_id, funding)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                description,
                amount,
                category_id,
                type_.value,
                month_ref,
                series_id,
                funding.value,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def update(
        self,
        transaction_id: int,
        description: str,
        amount: float,
        category_id: int,
        funding: FundingSource = FundingSource.SALARY,
    ) -> None:
        self._conn.execute(
            """UPDATE transactions
               SET description = ?, amount = ?, category_id = ?, funding = ?
               WHERE id = ?""",
            (description, amount, category_id, funding.value, transaction_id),
        )
        self._conn.commit()

    def update_series_forward(
        self,
        series_id: int,
        from_month: str,
        description: str,
        amount: float,
        category_id: int,
        funding: FundingSource = FundingSource.SALARY,
    ) -> None:
        """Edita a ocorrência do mês e as futuras já materializadas.

        Os meses anteriores ficam com o valor histórico.
        """
        self._conn.execute(
            """UPDATE transactions
               SET description = ?, amount = ?, category_id = ?, funding = ?
               WHERE series_id = ? AND month_ref >= ?""",
            (description, amount, category_id, funding.value, series_id, from_month),
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

    def total_by_funding(self, month_ref: str, funding: FundingSource) -> float:
        """Quanto saiu de cada carteira (salário, VR ou VA) no mês."""
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions "
            "WHERE month_ref = ? AND funding = ?",
            (month_ref, funding.value),
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

    def opened_months(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT month_ref FROM month_settings ORDER BY month_ref"
        ).fetchall()
        return [r["month_ref"] for r in rows]

    #: Coluna de month_settings e do profile correspondente a cada carteira.
    _COLUMNS = {
        FundingSource.SALARY: ("income", "monthly_income"),
        FundingSource.VR: ("vr", "vr_income"),
        FundingSource.VA: ("va", "va_income"),
    }

    def amount(self, month_ref: str, source: FundingSource) -> float:
        """Valor congelado da carteira no mes; cai para o padrao do perfil."""
        coluna, padrao = self._COLUMNS[source]
        row = self._conn.execute(
            f"SELECT {coluna} AS v FROM month_settings WHERE month_ref = ?", (month_ref,)
        ).fetchone()
        if row:
            return float(row["v"])
        default = self._conn.execute(
            f"SELECT {padrao} AS v FROM profile WHERE id = 1"
        ).fetchone()
        return float(default["v"]) if default else 0.0

    def income(self, month_ref: str) -> float:
        return self.amount(month_ref, FundingSource.SALARY)

    def ensure_month(self, month_ref: str) -> None:
        """Abre a competencia se ela ainda nao existir (virada de mes).

        - Congela a renda vigente do perfil para o mes.
        - Copia os lancamentos das series recorrentes ainda vigentes, ou seja,
          sem data final ou com data final igual/posterior a este mes.
        - Variaveis nao sao copiadas: zeram na virada.
        """
        if self.exists(month_ref):
            return

        p = self._conn.execute(
            "SELECT monthly_income, vr_income, va_income FROM profile WHERE id = 1"
        ).fetchone()
        self._conn.execute(
            "INSERT INTO month_settings (month_ref, income, vr, va) VALUES (?, ?, ?, ?)",
            (
                month_ref,
                float(p["monthly_income"]) if p else 0.0,
                float(p["vr_income"]) if p else 0.0,
                float(p["va_income"]) if p else 0.0,
            ),
        )

        previous = self._conn.execute(
            "SELECT MAX(month_ref) AS m FROM month_settings WHERE month_ref < ?",
            (month_ref,),
        ).fetchone()
        if previous and previous["m"]:
            placeholders = ",".join("?" for _ in RECURRING_TYPES)
            self._conn.execute(
                f"""INSERT INTO transactions
                        (description, amount, category_id, type, month_ref, series_id, funding)
                    SELECT t.description, t.amount, t.category_id, t.type, ?, t.series_id,
                           t.funding
                    FROM transactions t
                    JOIN series s ON s.id = t.series_id
                    WHERE t.month_ref = ?
                      AND t.type IN ({placeholders})
                      AND (s.end_month IS NULL OR s.end_month >= ?)""",
                (month_ref, previous["m"], *[t.value for t in RECURRING_TYPES], month_ref),
            )
        self._conn.commit()

    def apply_incomes_from(
        self, month_ref: str, income: float, vr: float, va: float
    ) -> None:
        """Propaga salario, VR e VA para o mes informado e todos os posteriores.

        Meses anteriores mantem os valores historicos congelados.
        """
        self._conn.execute(
            "UPDATE month_settings SET income = ?, vr = ?, va = ? WHERE month_ref >= ?",
            (income, vr, va, month_ref),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO month_settings (month_ref, income, vr, va) "
            "VALUES (?, ?, ?, ?)",
            (month_ref, income, vr, va),
        )
        self._conn.commit()
