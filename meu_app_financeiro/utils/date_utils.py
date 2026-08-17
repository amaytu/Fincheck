"""Manipulacao de competencias mensais no formato 'YYYY-MM'."""

from datetime import date

MONTHS_PT = [
    "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def current_month_key() -> str:
    """Competencia do mes corrente, ex: '2026-08'."""
    return month_key(date.today())


def month_key(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def split_key(key: str) -> tuple[int, int]:
    year, month = key.split("-")
    return int(year), int(month)


def shift_month(key: str, delta: int) -> str:
    """'2026-08' + 1 -> '2026-09'; '2026-01' - 1 -> '2025-12'."""
    year, month = split_key(key)
    index = (year * 12 + (month - 1)) + delta
    return f"{index // 12:04d}-{(index % 12) + 1:02d}"


def month_label(key: str) -> str:
    """'2026-08' -> 'Agosto 2026'."""
    year, month = split_key(key)
    return f"{MONTHS_PT[month - 1]} {year}"


def month_short_label(key: str) -> str:
    """'2026-08' -> 'Ago/2026'."""
    year, month = split_key(key)
    return f"{MONTHS_PT[month - 1][:3]}/{year}"


def month_options(start: str, months_ahead: int = 60) -> list[tuple[str, str]]:
    """Competencias de `start` em diante: [('2026-08', 'Agosto 2026'), ...].

    Usado no seletor "Repetir ate" do formulario de lancamento.
    """
    return [
        (key, month_label(key))
        for key in (shift_month(start, i) for i in range(months_ahead + 1))
    ]
