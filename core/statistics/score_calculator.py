# core/statistics/score_calculator.py

import math
from core.config.score_config import ScoreConfig


class ScoreCalculator:

    @staticmethod
    def score_frequencia(jogo, mapa_frequencia, max_freq):
        """
        Calcula score baseado na frequência histórica das dezenas.
        """
        soma_freq = sum(mapa_frequencia.get(d, 0) for d in jogo.dezenas)
        media_freq = soma_freq / len(jogo.dezenas)

        if max_freq == 0:
            return 0.0

        return media_freq / max_freq

    @staticmethod
    def score_soma(jogo):
        """
        Score gaussiano baseado na soma das dezenas.
        """
        diferenca = jogo.soma - ScoreConfig.MEDIA_SOMA
        return math.exp(-(diferenca ** 2) / (2 * (ScoreConfig.DESVIO_SOMA ** 2)))

    @staticmethod
    def score_pares(jogo):
        """
        Score gaussiano baseado na quantidade de pares.
        """
        diferenca = jogo.pares - ScoreConfig.MEDIA_PARES
        return math.exp(-(diferenca ** 2) / (2 * (ScoreConfig.DESVIO_PARES ** 2)))

    @staticmethod
    def score_atraso(jogo, mapa_atraso, max_atraso):
        """
        Score baseado no atraso das dezenas.
        """
        if max_atraso == 0:
            return 0.0

        soma_atraso = sum(mapa_atraso.get(d, 0) for d in jogo.dezenas)
        media_atraso = soma_atraso / len(jogo.dezenas)

        return media_atraso / max_atraso

    @classmethod
    def calcular_score(
        cls,
        jogo,
        mapa_frequencia,
        max_freq,
        mapa_atraso=None,
        max_atraso=1
    ):
        """
        Calcula score final ponderado do jogo.
        """

        sf = cls.score_frequencia(jogo, mapa_frequencia, max_freq)
        ss = cls.score_soma(jogo)
        sp = cls.score_pares(jogo)

        sa = 0.0
        if mapa_atraso:
            sa = cls.score_atraso(jogo, mapa_atraso, max_atraso)

        score_final = (
            ScoreConfig.PESO_FREQUENCIA * sf +
            ScoreConfig.PESO_SOMA * ss +
            ScoreConfig.PESO_PARES * sp +
            ScoreConfig.PESO_ATRASO * sa
        )

        return round(score_final, 6)