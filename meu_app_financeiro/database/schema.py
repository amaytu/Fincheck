"""DDL, inicialização e migração do banco."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    id             INTEGER PRIMARY KEY CHECK (id = 1),
    display_name   TEXT    NOT NULL DEFAULT 'Visitante',
    monthly_income REAL    NOT NULL DEFAULT 0,
    vr_income      REAL    NOT NULL DEFAULT 0,
    va_income      REAL    NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    color         TEXT NOT NULL,
    type          TEXT NOT NULL CHECK (type IN ('fixed', 'variable', 'investment')),
    meal_eligible INTEGER NOT NULL DEFAULT 0,
    UNIQUE (name, type)
);

-- Uma serie representa um lancamento recorrente ao longo dos meses.
-- end_month NULL = repete indefinidamente; caso contrario para nessa competencia.
CREATE TABLE IF NOT EXISTS series (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT NOT NULL CHECK (type IN ('fixed', 'variable', 'investment')),
    start_month TEXT NOT NULL,
    end_month   TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount      REAL NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    type        TEXT NOT NULL CHECK (type IN ('fixed', 'variable', 'investment')),
    month_ref   TEXT NOT NULL,
    funding     TEXT NOT NULL DEFAULT 'salary' CHECK (funding IN ('salary', 'vr', 'va')),
    series_id   INTEGER REFERENCES series(id) ON DELETE CASCADE,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Snapshot das entradas do mes: preserva o historico quando o usuario altera
-- os valores no perfil (a alteracao vale do mes atual em diante).
CREATE TABLE IF NOT EXISTS month_settings (
    month_ref TEXT PRIMARY KEY,
    income    REAL NOT NULL,
    vr        REAL NOT NULL DEFAULT 0,
    va        REAL NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_transactions_month ON transactions (month_ref, type);
"""

# Criado so depois da migracao: em bancos antigos a coluna ainda nao existe
# quando o SCHEMA acima roda.
INDEX_SERIES = (
    "CREATE INDEX IF NOT EXISTS idx_transactions_series ON transactions (series_id)"
)

#: Colunas adicionadas depois da primeira versao. ALTER TABLE nao aceita CHECK,
#: entao a restricao de `funding` so vale para bancos criados do zero.
NEW_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("profile", "vr_income", "REAL NOT NULL DEFAULT 0"),
    ("profile", "va_income", "REAL NOT NULL DEFAULT 0"),
    ("categories", "meal_eligible", "INTEGER NOT NULL DEFAULT 0"),
    ("transactions", "funding", "TEXT NOT NULL DEFAULT 'salary'"),
    ("month_settings", "vr", "REAL NOT NULL DEFAULT 0"),
    ("month_settings", "va", "REAL NOT NULL DEFAULT 0"),
)


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _migrate_series(conn: sqlite3.Connection) -> None:
    """Bancos criados antes da tabela `series` ganham a coluna e o vinculo.

    Cada grupo (descricao, categoria, tipo) de lancamento recorrente vira uma
    serie sem data final, preservando o comportamento que o usuario ja tinha.
    """
    if "series_id" in _columns(conn, "transactions"):
        return

    conn.execute("ALTER TABLE transactions ADD COLUMN series_id INTEGER REFERENCES series(id)")
    grupos = conn.execute(
        """SELECT description, category_id, type, MIN(month_ref) AS inicio
           FROM transactions
           WHERE type IN ('fixed', 'investment')
           GROUP BY description, category_id, type"""
    ).fetchall()
    for g in grupos:
        cursor = conn.execute(
            "INSERT INTO series (type, start_month, end_month) VALUES (?, ?, NULL)",
            (g["type"], g["inicio"]),
        )
        conn.execute(
            """UPDATE transactions SET series_id = ?
               WHERE description = ? AND category_id = ? AND type = ?""",
            (cursor.lastrowid, g["description"], g["category_id"], g["type"]),
        )
    conn.commit()


def _migrate_columns(conn: sqlite3.Connection) -> None:
    """Adiciona colunas novas a bancos ja existentes, uma a uma."""
    for table, column, definition in NEW_COLUMNS:
        if column not in _columns(conn, table):
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    conn.commit()


def init_db(conn: sqlite3.Connection) -> None:
    """Cria as tabelas (idempotente), migra e garante a linha unica de perfil."""
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR IGNORE INTO profile (id) VALUES (1)")
    conn.commit()
    _migrate_columns(conn)
    _migrate_series(conn)
    conn.execute(INDEX_SERIES)
    conn.commit()
