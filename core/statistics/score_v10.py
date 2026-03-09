# core/statistics/score_v10.py

from statistics import mean, pstdev


class ScoreV10:

    JANELA_CICLO = 50

    @staticmethod
    def normalizar(valor, max_valor):
        if max_valor == 0:
            return 0
        return valor / max_valor

    @classmethod
    def detectar_ciclo(cls, concursos):

        ultimos = concursos[-cls.JANELA_CICLO:]

        somas = [sum(c.dezenas) for c in ultimos]
        pares = [sum(1 for n in c.dezenas if n % 2 == 0) for c in ultimos]

        var_soma = pstdev(somas)
        var_pares = pstdev(pares)

        dezenas_rotativas = set()
        for c in ultimos:
            dezenas_rotativas.update(c.dezenas)

        rotatividade = len(dezenas_rotativas) / 25

        var_soma_norm = min(var_soma / 40, 1)
        var_pares_norm = min(var_pares / 5, 1)

        indice_volatilidade = (
            0.4 * var_soma_norm +
            0.3 * var_pares_norm +
            0.3 * rotatividade
        )

        if indice_volatilidade >= 0.6:
            ciclo = "AGRESSIVO"
            peso_recencia = 0.75
        elif indice_volatilidade <= 0.4:
            ciclo = "CONSERVADOR"
            peso_recencia = 0.50
        else:
            ciclo = "BALANCEADO"
            peso_recencia = 0.65

        return ciclo, indice_volatilidade, peso_recencia

    @classmethod
    def calcular(
        cls,
        jogo,
        concursos,
        mapa_freq_recente,
        mapa_atraso,
        max_freq,
        max_atraso
    ):

        ciclo, indice_volatilidade, peso_recencia = cls.detectar_ciclo(concursos)
        peso_historico = 1 - peso_recencia

        # Frequência histórica
        freq_hist = {n: 0 for n in range(1, 26)}
        for c in concursos:
            for d in c.dezenas:
                freq_hist[d] += 1

        max_hist = max(freq_hist.values())

        score_freq = 0
        score_atraso = 0

        for n in jogo.dezenas:

            freq_hibrida = (
                peso_recencia * cls.normalizar(mapa_freq_recente.get(n, 0), max_freq)
                + peso_historico * cls.normalizar(freq_hist[n], max_hist)
            )

            score_freq += freq_hibrida
            score_atraso += cls.normalizar(mapa_atraso.get(n, 0), max_atraso)

        # BÔNUS DE REPETIÇÃO (últimos 3 concursos)
        ultimos_3 = concursos[-3:]
        dezenas_ultimos = set()

        for c in ultimos_3:
            dezenas_ultimos.update(c.dezenas)

        repeticoes = len(set(jogo.dezenas) & dezenas_ultimos)

        if 8 <= repeticoes <= 10:
            bonus_repeticao = 0.15
        elif 6 <= repeticoes <= 7:
            bonus_repeticao = 0.05
        elif repeticoes >= 12:
            bonus_repeticao = -0.10
        else:
            bonus_repeticao = 0

        score_final = (
            0.60 * score_freq +
            0.25 * score_atraso +
            bonus_repeticao
        )

        return score_final, ciclo, indice_volatilidade, peso_recencia, repeticoes