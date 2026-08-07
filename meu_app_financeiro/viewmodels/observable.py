"""Base minima de estado reativo.

As Views registram um callback; qualquer mutacao no ViewModel dispara
notify() e a tela se redesenha. E o que faz a Tela 1 refletir na hora as
alteracoes salvas na Tela 3.
"""

from collections.abc import Callable

Listener = Callable[[], None]


class Observable:
    def __init__(self) -> None:
        self._listeners: list[Listener] = []

    def add_listener(self, listener: Listener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def notify(self) -> None:
        for listener in list(self._listeners):
            listener()
