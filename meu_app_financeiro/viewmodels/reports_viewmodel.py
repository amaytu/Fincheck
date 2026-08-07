"""ViewModel da Tela 2 (Relatorios)."""

from models import TransactionType
from utils import format_compact, month_label, shift_month

from .app_state import AppState
from .observable import Observable

SECTION_ORDER = (TransactionType.FIXED, TransactionType.VARIABLE, TransactionType.INVESTMENT)

#: Cor macro de cada grupo no grafico de rosca.
GROUP_COLORS = {
    TransactionType.FIXED: "#EF5350",
    TransactionType.VARIABLE: "#42A5F5",
    TransactionType.INVESTMENT: "#66BB6A",
}


class ReportsViewModel(Observable):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.month_ref = state.current_month
        self.state.add_listener(self.notify)

    # --------------------------------------------------------------- navegacao
    @property
    def month_title(self) -> str:
        return month_label(self.month_ref)

    def go_previous_month(self) -> None:
        self._go(shift_month(self.month_ref, -1))

    def go_next_month(self) -> None:
        self._go(shift_month(self.month_ref, 1))

    def _go(self, month_ref: str) -> None:
        self.state.open_month(month_ref)  # materializa a competencia se for nova
        self.month_ref = month_ref
        self.notify()

    # ------------------------------------------------------------------ dados
    @property
    def total(self) -> float:
        return self.state.transactions.total_of_month(self.month_ref)

    @property
    def total_label(self) -> str:
        return format_compact(self.total)

    @property
    def has_data(self) -> bool:
        return self.total > 0

    def group_totals(self) -> list[dict]:
        """Fatias do grafico macro: [{type, label, total, color, ratio}, ...]."""
        total = self.total
        result = []
        for type_ in SECTION_ORDER:
            value = self.state.transactions.total_by_type(self.month_ref, type_)
            result.append(
                {
                    "type": type_,
                    "label": type_.label,
                    "total": value,
                    "color": GROUP_COLORS[type_],
                    "ratio": (value / total) if total else 0.0,
                }
            )
        return result

    def breakdown_of(self, type_: TransactionType) -> list[dict]:
        """Detalhamento por categoria, com a barra proporcional ao maior item."""
        rows = self.state.transactions.totals_by_category(self.month_ref, type_)
        largest = max((r["total"] for r in rows), default=0.0)
        for row in rows:
            row["ratio"] = (row["total"] / largest) if largest else 0.0
        return rows

    def dispose(self) -> None:
        self.state.remove_listener(self.notify)
