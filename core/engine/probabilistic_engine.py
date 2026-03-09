# core/engine/probabilistic_engine.py

import random
from core.domain.value_objects import Jogo
from core.statistics.score_v10 import ScoreV10


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
        candidatos=500,
        modo_score=None  # Mantido para compatibilidade com main/backtest
    ):

        mapa_freq = cls.gerar_mapa_frequencia_recente(concursos)
        max_freq = max(mapa_freq.values()) if mapa_freq else 1

        mapa_atraso = cls.gerar_mapa_atraso(concursos)
        max_atraso = max(mapa_atraso.values()) if mapa_atraso else 1

        jogos_candidatos = []

        ciclo_detectado = None
        indice_volatilidade = None
        peso_recencia = None

        for _ in range(candidatos):

            dezenas = tuple(sorted(random.sample(range(1, 26), 15)))
            jogo = Jogo(dezenas)

            score, ciclo, indice, peso, repeticoes = ScoreV10.calcular(
                jogo,
                concursos,
                mapa_freq,
                mapa_atraso,
                max_freq,
                max_atraso
            )

            if ciclo_detectado is None:
                ciclo_detectado = ciclo
                indice_volatilidade = indice
                peso_recencia = peso

            jogos_candidatos.append((jogo, score, repeticoes))

        jogos_candidatos.sort(key=lambda x: x[1], reverse=True)

        print("\nCICLO DETECTADO PELO SISTEMA:")
        print(f"Tipo: {ciclo_detectado}")
        print(f"Índice de Volatilidade: {round(indice_volatilidade, 3)}")
        print(f"Peso Recência Aplicado: {round(peso_recencia, 2)}")
        print("-" * 60)

        return jogos_candidatos[:quantidade]