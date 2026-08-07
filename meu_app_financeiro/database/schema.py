"""DDL e inicializacao do banco."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    id             INTEGER PRIMARY KEY CHECK (id = 1),
    display_name   TEXT    NOT NULL DEFAULT 'Visitante',
    monthly_income REAL    NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    color TEXT NOT NULL,
    type  TEXT NOT NULL CHECK (type IN ('fixed', 'variable', 'investment')),
    UNIQUE (name, type)
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount      REAL NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    type        TEXT NOT NULL CHECK (type IN ('fixed', 'variable', 'investment')),
    month_ref   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Snapshot da renda por competencia: preserva o historico quando o usuario
-- altera a renda no perfil (a alteracao vale do mes atual em diante).
CREATE TABLE IF NOT EXISTS month_settings (
    month_ref TEXT PRIMARY KEY,
    income    REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_month ON transactions (month_ref, type);
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Cria as tabelas (idempotente) e garante a linha unica de perfil."""
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR IGNORE INTO profile (id) VALUES (1)")
    conn.commit()
