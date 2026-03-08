# core/engine/probabilistic_engine.py

import random
from core.domain.value_objects import Jogo
from core.statistics.score_calculator import ScoreCalculator
from core.statistics.score_v9 import ScoreV9


class ProbabilisticEngine:

    JANELA_RECENCIA = 200

    @staticmethod
    def gerar_mapa_frequencia_recente(concursos):
        mapa = {}
        concursos_recente = concursos[-ProbabilisticEngine.JANELA_RECENCIA:]
        total = len(concursos_recente)

        for i, concurso in enumerate(concursos_recente):
            peso = (i + 1) / total
            for dezena in concurso.dezenas:
                mapa[dezena] = mapa.get(dezena, 0) + peso

        return mapa

    @staticmethod
    def gerar_mapa_atraso(concursos):
        mapa = {i: 0 for i in range(1, 26)}

        for concurso in reversed(concursos):
            for dezena in mapa:
                if dezena in concurso.dezenas:
                    mapa[dezena] = 0
                else:
                    mapa[dezena] += 1

        return mapa

    @classmethod
    def gerar_jogos(
        cls,
        concursos,
        quantidade=5,
        candidatos=200,
        modo_score="v7"
    ):

        mapa_freq = cls.gerar_mapa_frequencia_recente(concursos)
        max_freq = max(mapa_freq.values()) if mapa_freq else 1

        mapa_atraso = cls.gerar_mapa_atraso(concursos)
        max_atraso = max(mapa_atraso.values()) if mapa_atraso else 1

        jogos_candidatos = []

        for _ in range(candidatos):

            dezenas = tuple(sorted(random.sample(range(1, 26), 15)))
            jogo = Jogo(dezenas)

            if modo_score == "v9":
                score = ScoreV9.calcular(jogo.dezenas, concursos)

            else:  # V7 padrão
                score = ScoreCalculator.calcular_score(
                    jogo,
                    mapa_freq,
                    max_freq,
                    mapa_atraso,
                    max_atraso
                )

            jogos_candidatos.append((jogo, score))

        jogos_candidatos.sort(key=lambda x: x[1], reverse=True)

        return jogos_candidatos[:quantidade]