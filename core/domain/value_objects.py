# core/domain/value_objects.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Jogo:
    """
    Value Object imutável.
    Representa uma combinação de 15 números.
    """

    dezenas: Tuple[int, ...]

    def __post_init__(self):
        if len(self.dezenas) != 15:
            raise ValueError("Um jogo deve conter exatamente 15 dezenas.")

        if len(set(self.dezenas)) != 15:
            raise ValueError("As dezenas devem ser únicas.")

        for dezena in self.dezenas:
            if dezena < 1 or dezena > 25:
                raise ValueError("As dezenas devem estar entre 1 e 25.")

    @property
    def soma(self) -> int:
        return sum(self.dezenas)

    @property
    def pares(self) -> int:
        return len([d for d in self.dezenas if d % 2 == 0])

    @property
    def impares(self) -> int:
        return 15 - self.pares