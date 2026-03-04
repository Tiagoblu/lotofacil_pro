# core/domain/models.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Concurso:
    """
    Entidade principal do domínio.
    Representa um sorteio oficial da Lotofácil.
    """

    numero: int
    data: str
    dezenas: Tuple[int, ...]

    def __post_init__(self):
        if len(self.dezenas) != 15:
            raise ValueError("Um concurso deve conter exatamente 15 dezenas.")

        if len(set(self.dezenas)) != 15:
            raise ValueError("As dezenas devem ser únicas.")

        for dezena in self.dezenas:
            if dezena < 1 or dezena > 25:
                raise ValueError("As dezenas devem estar no intervalo de 1 a 25.")