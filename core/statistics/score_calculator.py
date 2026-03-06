# core/statistics/score_calculator.py

import math
from core.config.score_config import ScoreConfig


class ScoreCalculator:

    # -----------------------------
    # Frequência histórica
    # -----------------------------
    @staticmethod
    def score_frequencia(jogo, mapa_frequencia, max_freq):

        soma_freq = sum(mapa_frequencia.get(d, 0) for d in jogo.dezenas)
        media_freq = soma_freq / len(jogo.dezenas)

        if max_freq == 0:
            return 0.0

        return media_freq / max_freq


    # -----------------------------
    # Soma das dezenas
    # -----------------------------
    @staticmethod
    def score_soma(jogo):

        diferenca = jogo.soma - ScoreConfig.MEDIA_SOMA

        return math.exp(
            -(diferenca ** 2) /
            (2 * (ScoreConfig.DESVIO_SOMA ** 2))
        )


    # -----------------------------
    # Quantidade de pares
    # -----------------------------
    @staticmethod
    def score_pares(jogo):

        diferenca = jogo.pares - ScoreConfig.MEDIA_PARES

        return math.exp(
            -(diferenca ** 2) /
            (2 * (ScoreConfig.DESVIO_PARES ** 2))
        )


    # -----------------------------
    # Atraso médio das dezenas
    # -----------------------------
    @staticmethod
    def score_atraso(jogo, mapa_atraso, max_atraso):

        if max_atraso == 0:
            return 0.0

        soma_atraso = sum(mapa_atraso.get(d, 0) for d in jogo.dezenas)

        media_atraso = soma_atraso / len(jogo.dezenas)

        return media_atraso / max_atraso


    # -----------------------------
    # Distribuição por linhas
    # -----------------------------
    @staticmethod
    def score_distribuicao(jogo):

        linhas = [0, 0, 0, 0, 0]

        for d in jogo.dezenas:

            if d <= 5:
                linhas[0] += 1
            elif d <= 10:
                linhas[1] += 1
            elif d <= 15:
                linhas[2] += 1
            elif d <= 20:
                linhas[3] += 1
            else:
                linhas[4] += 1

        ideal = 3

        erro = sum(abs(l - ideal) for l in linhas)

        return 1 / (1 + erro)


    # -----------------------------
    # Penalização de sequência
    # -----------------------------
    @staticmethod
    def penalidade_sequencia(jogo):

        dezenas = sorted(jogo.dezenas)

        maior_seq = 1
        atual = 1

        for i in range(1, len(dezenas)):

            if dezenas[i] == dezenas[i - 1] + 1:
                atual += 1
                maior_seq = max(maior_seq, atual)
            else:
                atual = 1

        if maior_seq >= 6:
            return ScoreConfig.PENALIDADE_EXTREMO

        return 0


    # -----------------------------
    # Score final
    # -----------------------------
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

        penalidade = cls.penalidade_sequencia(jogo)

        score_final = (
            ScoreConfig.PESO_FREQUENCIA * sf +
            ScoreConfig.PESO_SOMA * ss +
            ScoreConfig.PESO_PARES * sp +
            ScoreConfig.PESO_ATRASO * sa +
            sd
        ) - penalidade

        return round(score_final, 6)