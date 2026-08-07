"""Conexao com o SQLite local."""

import os
import sqlite3
from pathlib import Path

DB_FILENAME = "financeiro.db"


def database_path() -> Path:
    """Diretorio gravavel do app.

    No Android o Flet expoe FLET_APP_STORAGE_DATA (unico caminho com permissao
    de escrita). No desktop, cai para a pasta do projeto.
    """
    storage = os.getenv("FLET_APP_STORAGE_DATA")
    base = Path(storage) if storage else Path(__file__).resolve().parent.parent
    base.mkdir(parents=True, exist_ok=True)
    return base / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    """Nova conexao com row_factory e FKs habilitadas."""
    conn = sqlite3.connect(database_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
