# core/statistics/score_v9.py

from statistics import mean


class ScoreV9:

    JANELA_RECENTE = 200
    JANELA_ESTRUTURAL = 50

    @staticmethod
    def normalizar(valor, max_valor):
        if max_valor == 0:
            return 0
        return valor / max_valor

    @classmethod
    def calcular(cls, jogo, concursos):

        # =========================
        # Frequência Histórica
        # =========================
        freq_hist = {n: 0 for n in range(1, 26)}
        for c in concursos:
            for d in c.dezenas:
                freq_hist[d] += 1

        max_hist = max(freq_hist.values())

        # =========================
        # Frequência Recente
        # =========================
        recentes = concursos[-cls.JANELA_RECENTE:]
        freq_rec = {n: 0 for n in range(1, 26)}
        for c in recentes:
            for d in c.dezenas:
                freq_rec[d] += 1

        max_rec = max(freq_rec.values())

        # =========================
        # Atraso
        # =========================
        atraso = {n: 0 for n in range(1, 26)}
        for c in reversed(concursos):
            for n in atraso:
                if n in c.dezenas:
                    atraso[n] = 0
                else:
                    atraso[n] += 1

        max_atraso = max(atraso.values())

        # =========================
        # Frequência híbrida
        # =========================
        score_freq = 0
        score_atraso = 0

        for n in jogo:

            freq_hibrida = (
                0.6 * cls.normalizar(freq_rec[n], max_rec)
                + 0.4 * cls.normalizar(freq_hist[n], max_hist)
            )

            score_freq += freq_hibrida
            score_atraso += cls.normalizar(atraso[n], max_atraso)

        # =========================
        # Ajuste estrutural recente
        # =========================
        estruturais = concursos[-cls.JANELA_ESTRUTURAL:]

        medias_soma = [sum(c.dezenas) for c in estruturais]
        media_soma_recente = mean(medias_soma)

        soma_jogo = sum(jogo)
        ajuste_soma = 1 - abs(soma_jogo - media_soma_recente) / 200
        ajuste_soma = max(0, ajuste_soma)

        pares_jogo = sum(1 for n in jogo if n % 2 == 0)

        medias_pares = [
            sum(1 for n in c.dezenas if n % 2 == 0)
            for c in estruturais
        ]

        media_pares_recente = mean(medias_pares)

        ajuste_paridade = 1 - abs(pares_jogo - media_pares_recente) / 15
        ajuste_paridade = max(0, ajuste_paridade)

        # =========================
        # Distribuição por faixa
        # =========================
        faixas = [
            range(1, 6),
            range(6, 11),
            range(11, 16),
            range(16, 21),
            range(21, 26)
        ]

        distribuicao_score = 0
        for faixa in faixas:
            qtd = sum(1 for n in jogo if n in faixa)
            distribuicao_score += 1 - abs(qtd - 3) / 5

        distribuicao_score /= 5

        # =========================
        # Score Final V9
        # =========================
        score_final = (
            0.40 * score_freq +
            0.20 * score_atraso +
            0.15 * ajuste_paridade +
            0.15 * ajuste_soma +
            0.10 * distribuicao_score
        )

        return score_final