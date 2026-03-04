# core/statistics/metrics.py

from typing import List
from statistics import mean
from core.domain.models import Concurso


class MetricsCalculator:

    @staticmethod
    def media_soma(concursos: List[Concurso]) -> float:
        """
        Calcula média da soma das dezenas
        considerando todos os concursos.
        """
        somas = [sum(c.dezenas) for c in concursos]
        return mean(somas) if somas else 0.0

    @staticmethod
    def media_pares(concursos: List[Concurso]) -> float:
        """
        Calcula média de números pares
        considerando todos os concursos.
        """
        pares = [sum(1 for d in c.dezenas if d % 2 == 0) for c in concursos]
        return mean(pares) if pares else 0.0