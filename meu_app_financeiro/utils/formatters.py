"""Formatacao de moeda e numeros no padrao brasileiro (pt-BR)."""

import re

_CURRENCY_CLEANUP = re.compile(r"[^\d,.-]")


def format_currency(value: float, symbol: bool = True) -> str:
    """1234.5 -> 'R$ 1.234,50'."""
    negative = value < 0
    formatted = f"{abs(value):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    prefix = "R$ " if symbol else ""
    return f"{'-' if negative else ''}{prefix}{formatted}"


def format_compact(value: float) -> str:
    """1234.5 -> 'R$ 1,2 mil' (usado no centro do grafico)."""
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f}".replace(".", ",") + " mi"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.1f}".replace(".", ",") + " mil"
    return format_currency(value)


def parse_currency(text: str) -> float:
    """Aceita '1.234,50', '1234.50', 'R$ 90' -> float. Retorna 0.0 se invalido."""
    if text is None:
        return 0.0
    cleaned = _CURRENCY_CLEANUP.sub("", str(text)).strip()
    if not cleaned:
        return 0.0
    # Se tem virgula, ela e o separador decimal (padrao BR).
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return 0.0


def format_percent(value: float, total: float) -> str:
    if not total:
        return "0%"
    return f"{(value / total) * 100:.0f}%"


def safe_ratio(value: float, total: float) -> float:
    """Proporcao entre 0.0 e 1.0, protegida contra divisao por zero."""
    if not total:
        return 0.0
    return max(0.0, min(1.0, value / total))
