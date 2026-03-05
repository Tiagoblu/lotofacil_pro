import math
from core.config.score_config import ScoreConfig


class ScoreCalculator:

    # =====================================
    # FREQUÊNCIA
    # =====================================

    @staticmethod
    def score_frequencia(jogo, mapa_frequencia, max_freq):

        soma_freq = sum(mapa_frequencia.get(d, 0) for d in jogo.dezenas)
        media_freq = soma_freq / len(jogo.dezenas)

        if max_freq == 0:
            return 0.0

        return media_freq / max_freq

    # =====================================
    # SOMA
    # =====================================

    @staticmethod
    def score_soma(jogo):

        diferenca = jogo.soma - ScoreConfig.MEDIA_SOMA

        return math.exp(
            -(diferenca ** 2) /
            (2 * (ScoreConfig.DESVIO_SOMA ** 2))
        )

    # =====================================
    # PARES
    # =====================================

    @staticmethod
    def score_pares(jogo):

        diferenca = jogo.pares - ScoreConfig.MEDIA_PARES

        return math.exp(
            -(diferenca ** 2) /
            (2 * (ScoreConfig.DESVIO_PARES ** 2))
        )

    # =====================================
    # ATRASO
    # =====================================

    @staticmethod
    def score_atraso(jogo, mapa_atraso, max_atraso):

        if max_atraso == 0:
            return 0.0

        soma_atraso = sum(mapa_atraso.get(d, 0) for d in jogo.dezenas)
        media_atraso = soma_atraso / len(jogo.dezenas)

        return media_atraso / max_atraso

    # =====================================
    # DISTRIBUIÇÃO BAIXAS / ALTAS
    # =====================================

    @staticmethod
    def score_distribuicao(jogo):

        baixas = len([d for d in jogo.dezenas if d <= 13])
        altas = len([d for d in jogo.dezenas if d > 13])

        diferenca = abs(baixas - altas)

        # distribuição ideal ~ 7 / 8
        return math.exp(-(diferenca ** 2) / 8)

    # =====================================
    # PENALIDADE EXTREMOS
    # =====================================

    @staticmethod
    def penalidade_extremos(jogo):

        if jogo.soma < 150 or jogo.soma > 240:
            return ScoreConfig.PENALIDADE_EXTREMO

        if jogo.pares < 4 or jogo.pares > 11:
            return ScoreConfig.PENALIDADE_EXTREMO

        return 0.0

    # =====================================
    # SCORE FINAL
    # =====================================

    @classmethod
    def calcular_score(
        cls,
        jogo,
        mapa_frequencia,
        max_freq,
        mapa_atraso=None,
        max_atraso=1
    ):

        sf = cls.score_frequencia(jogo, mapa_frequencia, max_freq)
        ss = cls.score_soma(jogo)
        sp = cls.score_pares(jogo)

        sa = 0.0
        if mapa_atraso:
            sa = cls.score_atraso(jogo, mapa_atraso, max_atraso)

        sd = cls.score_distribuicao(jogo)

        penalidade = cls.penalidade_extremos(jogo)

        score_final = (
            ScoreConfig.PESO_FREQUENCIA * sf +
            ScoreConfig.PESO_SOMA * ss +
            ScoreConfig.PESO_PARES * sp +
            ScoreConfig.PESO_ATRASO * sa +
            sd
        ) - penalidade

        return round(score_final, 6)