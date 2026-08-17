"""Tokens visuais do app (Clean UI / Material 3)."""

import re

import flet as ft

# --- Paleta da marca Fincheck -----------------------------------------------
# Amostradas diretamente da arte oficial (assets/banner.png).
PRIMARY = "#104535"       # verde Fincheck
PRIMARY_DARK = "#0A2E23"
ACCENT = "#CDAD56"        # dourado Fincheck
GOLD = "#CDAD56"
GOLD_SOFT = "#E2CA8A"
ON_PRIMARY_MUTED = "#9FBFB2"  # texto secundario sobre o verde
BACKGROUND = "#F4F6F8"
SURFACE = "#FFFFFF"
TEXT = "#16202A"
TEXT_MUTED = "#7B8794"
DIVIDER = "#E8ECF1"
TRACK = "#EDF1F5"
DANGER = "#E53935"
POSITIVE = "#2E7D32"

# --- Metricas ---------------------------------------------------------------
RADIUS = 18
RADIUS_SM = 12
PAGE_PADDING = 16
GAP = 12

# --- Cores sugeridas ao criar uma categoria ---------------------------------
PRESET_COLORS = [
    "#EF5350", "#FF7043", "#FFA726", "#FFCA28",
    "#66BB6A", "#26A69A", "#42A5F5", "#5C6BC0",
    "#AB47BC", "#EC407A", "#8D6E63", "#78909C",
]

_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def normalize_hex(value: str, fallback: str = "#9E9E9E") -> str:
    """Valida e normaliza uma cor HEX digitada pelo usuário."""
    if not value:
        return fallback
    candidate = value.strip()
    if not candidate.startswith("#"):
        candidate = "#" + candidate
    if not _HEX_RE.match(candidate):
        return fallback
    if len(candidate) == 4:  # #abc -> #aabbcc
        candidate = "#" + "".join(ch * 2 for ch in candidate[1:])
    return candidate.upper()


def card(content: ft.Control, **kwargs) -> ft.Container:
    """Container padrão de cartão: fundo branco, cantos suaves e sombra leve."""
    kwargs.setdefault("padding", ft.padding.all(16))
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border_radius=RADIUS,
        shadow=ft.BoxShadow(
            blur_radius=18,
            spread_radius=0,
            color="#12000000",
            offset=ft.Offset(0, 6),
        ),
        **kwargs,
    )


def color_dot(color: str, size: int = 12) -> ft.Container:
    return ft.Container(
        width=size,
        height=size,
        bgcolor=color,
        border_radius=size,
    )


def app_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=PRIMARY,
        use_material3=True,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
