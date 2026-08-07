"""Dados falsos (mock) usados apenas na primeira execucao.

Toda a UI le do SQLite; este arquivo existe so para popular o banco vazio e
permitir visualizar o front-end com conteudo realista. Para comecar do zero,
apague o arquivo financeiro.db.
"""

import sqlite3

from models import TransactionType
from utils import current_month_key, shift_month

MOCK_PROFILE = {"display_name": "Gabriel", "monthly_income": 7500.00}

# (nome, cor HEX, tipo)
MOCK_CATEGORIES = [
    ("Moradia", "#EF5350", TransactionType.FIXED),
    ("Contas", "#FF7043", TransactionType.FIXED),
    ("Transporte", "#FFA726", TransactionType.FIXED),
    ("Alimentação", "#26A69A", TransactionType.VARIABLE),
    ("Lazer", "#42A5F5", TransactionType.VARIABLE),
    ("Saúde", "#EC407A", TransactionType.VARIABLE),
    ("Aposentadoria", "#66BB6A", TransactionType.INVESTMENT),
    ("Reserva de Emergência", "#8D6E63", TransactionType.INVESTMENT),
    ("Renda Variável", "#AB47BC", TransactionType.INVESTMENT),
]

# (descricao, valor, nome da categoria, tipo)
MOCK_TRANSACTIONS = [
    ("Aluguel", 1800.00, "Moradia", TransactionType.FIXED),
    ("Condomínio", 420.00, "Moradia", TransactionType.FIXED),
    ("Luz", 180.00, "Contas", TransactionType.FIXED),
    ("Internet", 120.00, "Contas", TransactionType.FIXED),
    ("Combustível", 350.00, "Transporte", TransactionType.FIXED),
    ("Mercado", 890.00, "Alimentação", TransactionType.VARIABLE),
    ("Restaurantes", 310.00, "Alimentação", TransactionType.VARIABLE),
    ("Cinema e streaming", 145.00, "Lazer", TransactionType.VARIABLE),
    ("Farmácia", 95.00, "Saúde", TransactionType.VARIABLE),
    ("Previdência privada", 600.00, "Aposentadoria", TransactionType.INVESTMENT),
    ("CDB liquidez diária", 450.00, "Reserva de Emergência", TransactionType.INVESTMENT),
    ("ETF BOVA11", 300.00, "Renda Variável", TransactionType.INVESTMENT),
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
        "UPDATE profile SET display_name = ?, monthly_income = ? WHERE id = 1",
        (MOCK_PROFILE["display_name"], MOCK_PROFILE["monthly_income"]),
    )

    category_ids: dict[str, int] = {}
    for name, color, type_ in MOCK_CATEGORIES:
        cursor = conn.execute(
            "INSERT INTO categories (name, color, type) VALUES (?, ?, ?)",
            (name, color, type_.value),
        )
        category_ids[name] = cursor.lastrowid

    this_month = current_month_key()
    last_month = shift_month(this_month, -1)

    for month_ref, factor in ((last_month, PREVIOUS_MONTH_FACTOR), (this_month, 1.0)):
        conn.execute(
            "INSERT OR REPLACE INTO month_settings (month_ref, income) VALUES (?, ?)",
            (month_ref, MOCK_PROFILE["monthly_income"]),
        )
        for description, amount, category_name, type_ in MOCK_TRANSACTIONS:
            conn.execute(
                """INSERT INTO transactions (description, amount, category_id, type, month_ref)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    description,
                    round(amount * factor, 2),
                    category_ids[category_name],
                    type_.value,
                    month_ref,
                ),
            )

    conn.commit()
