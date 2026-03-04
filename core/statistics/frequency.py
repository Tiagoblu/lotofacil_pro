# core/statistics/frequency.py

from collections import Counter
from typing import List, Dict
from core.domain.models import Concurso


class FrequencyCalculator:

    @staticmethod
    def calcular_frequencia(concursos: List[Concurso]) -> Dict[int, int]:
        """
        Calcula a frequência absoluta de cada dezena (1–25)
        considerando todos os concursos fornecidos.
        """

        contador = Counter()

        for concurso in concursos:
            contador.update(concurso.dezenas)

        # Garante presença de todos os números 1–25
        for numero in range(1, 26):
            contador.setdefault(numero, 0)

        return dict(sorted(contador.items()))