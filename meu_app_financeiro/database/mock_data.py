"""Dados falsos (mock) para desenvolvimento.

NAO e aplicado por padrao: o app nasce zerado. Para ver a interface preenchida,
rode com a variavel de ambiente FINCHECK_SEED=1.
"""

import sqlite3

from models import RECURRING_TYPES, FundingSource, TransactionType
from utils import current_month_key, shift_month

MOCK_PROFILE = {
    "display_name": "Gabriel",
    "monthly_income": 7500.00,
    "vr_income": 800.00,
    "va_income": 600.00,
}

# (nome, cor HEX, tipo, aceita VR/VA)
MOCK_CATEGORIES = [
    ("Moradia", "#EF5350", TransactionType.FIXED, False),
    ("Contas", "#FF7043", TransactionType.FIXED, False),
    ("Transporte", "#FFA726", TransactionType.FIXED, False),
    ("Refeição no trabalho", "#8D6E63", TransactionType.FIXED, True),
    ("Alimentação", "#26A69A", TransactionType.VARIABLE, True),
    ("Lazer", "#42A5F5", TransactionType.VARIABLE, False),
    ("Saúde", "#EC407A", TransactionType.VARIABLE, False),
    ("Aposentadoria", "#66BB6A", TransactionType.INVESTMENT, False),
    ("Reserva de Emergência", "#8D6E63", TransactionType.INVESTMENT, False),
    ("Renda Variável", "#AB47BC", TransactionType.INVESTMENT, False),
]

# (descricao, valor, categoria, tipo, carteira)
MOCK_TRANSACTIONS = [
    ("Aluguel", 1800.00, "Moradia", TransactionType.FIXED, FundingSource.SALARY),
    ("Condomínio", 420.00, "Moradia", TransactionType.FIXED, FundingSource.SALARY),
    ("Luz", 180.00, "Contas", TransactionType.FIXED, FundingSource.SALARY),
    ("Internet", 120.00, "Contas", TransactionType.FIXED, FundingSource.SALARY),
    ("Combustível", 350.00, "Transporte", TransactionType.FIXED, FundingSource.SALARY),
    ("Almoço no escritório", 450.00, "Refeição no trabalho", TransactionType.FIXED, FundingSource.VR),
    ("Mercado", 520.00, "Alimentação", TransactionType.VARIABLE, FundingSource.VA),
    ("Restaurantes", 310.00, "Alimentação", TransactionType.VARIABLE, FundingSource.VR),
    ("Padaria", 90.00, "Alimentação", TransactionType.VARIABLE, FundingSource.SALARY),
    ("Cinema e streaming", 145.00, "Lazer", TransactionType.VARIABLE, FundingSource.SALARY),
    ("Farmácia", 95.00, "Saúde", TransactionType.VARIABLE, FundingSource.SALARY),
    ("Previdência privada", 600.00, "Aposentadoria", TransactionType.INVESTMENT, FundingSource.SALARY),
    ("CDB liquidez diária", 450.00, "Reserva de Emergência", TransactionType.INVESTMENT, FundingSource.SALARY),
    ("ETF BOVA11", 300.00, "Renda Variável", TransactionType.INVESTMENT, FundingSource.SALARY),
]

# Ajuste aplicado ao mes anterior, so para o grafico da Tela 2 variar entre meses.
PREVIOUS_MONTH_FACTOR = 0.85


def is_empty(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT COUNT(*) AS n FROM categories").fetchone()
    return row["n"] == 0


def seed(conn: sqlite3.Connection) -> None:
    """Popula perfil, categorias e lancamentos do mes atual e do anterior."""
    if not is_empty(conn):
        return

    conn.execute(
        """UPDATE profile
           SET display_name = ?, monthly_income = ?, vr_income = ?, va_income = ?
           WHERE id = 1""",
        (
            MOCK_PROFILE["display_name"],
            MOCK_PROFILE["monthly_income"],
            MOCK_PROFILE["vr_income"],
            MOCK_PROFILE["va_income"],
        ),
    )

    category_ids: dict[str, int] = {}
    for name, color, type_, meal in MOCK_CATEGORIES:
        cursor = conn.execute(
            "INSERT INTO categories (name, color, type, meal_eligible) VALUES (?, ?, ?, ?)",
            (name, color, type_.value, int(meal)),
        )
        category_ids[name] = cursor.lastrowid

    this_month = current_month_key()
    last_month = shift_month(this_month, -1)

    # Cada lancamento recorrente ganha uma serie sem data final, para que o
    # rollover consiga copia-lo adiante.
    series_ids: dict[str, int] = {}
    for description, _amount, _category, type_, _funding in MOCK_TRANSACTIONS:
        if type_ in RECURRING_TYPES:
            cursor = conn.execute(
                "INSERT INTO series (type, start_month, end_month) VALUES (?, ?, NULL)",
                (type_.value, last_month),
            )
            series_ids[description] = cursor.lastrowid

    for month_ref, factor in ((last_month, PREVIOUS_MONTH_FACTOR), (this_month, 1.0)):
        conn.execute(
            "INSERT OR REPLACE INTO month_settings (month_ref, income, vr, va) "
            "VALUES (?, ?, ?, ?)",
            (
                month_ref,
                MOCK_PROFILE["monthly_income"],
                MOCK_PROFILE["vr_income"],
                MOCK_PROFILE["va_income"],
            ),
        )
        for description, amount, category_name, type_, funding in MOCK_TRANSACTIONS:
            conn.execute(
                """INSERT INTO transactions
                       (description, amount, category_id, type, month_ref, series_id, funding)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    description,
                    round(amount * factor, 2),
                    category_ids[category_name],
                    type_.value,
                    month_ref,
                    series_ids.get(description),
                    funding.value,
                ),
            )

    conn.commit()
