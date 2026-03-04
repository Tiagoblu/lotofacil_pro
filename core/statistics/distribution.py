# core/statistics/distribution.py

from typing import List
from core.domain.models import Concurso


class DistributionCalculator:

    @staticmethod
    def distribuicao_pares(concursos: List[Concurso]) -> List[int]:
        """
        Retorna lista contendo quantidade de pares
        em cada concurso.
        """
        return [
            sum(1 for d in concurso.dezenas if d % 2 == 0)
            for concurso in concursos
        ]

    @staticmethod
    def distribuicao_soma(concursos: List[Concurso]) -> List[int]:
        """
        Retorna lista com soma das dezenas
        de cada concurso.
        """
        return [
            sum(concurso.dezenas)
            for concurso in concursos
        ]