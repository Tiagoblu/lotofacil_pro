# core/engine/probabilistic_engine.py

import random
from typing import List, Tuple
from core.domain.models import Concurso


class ProbabilisticEngine:

    @staticmethod
    def gerar_jogos(
        concursos: List[Concurso],
        quantidade: int = 5,
        candidatos: int = 300,
        modo: str = "BALANCEADO"
    ) -> List[Tuple[Concurso, float, int]]:

        ultimo_concurso = concursos[-1]
        dezenas_ultimo = set(ultimo_concurso.dezenas)

        configuracoes = {
            "CONSERVADOR": {
                "max_repeticoes": 9,
                "peso_recencia": 0.55,
                "penalizacao": 0.15
            },
            "BALANCEADO": {
                "max_repeticoes": 11,
                "peso_recencia": 0.65,
                "penalizacao": 0.10
            },
            "AGRESSIVO": {
                "max_repeticoes": 13,
                "peso_recencia": 0.75,
                "penalizacao": 0.05
            }
        }

        config = configuracoes.get(modo.upper(), configuracoes["BALANCEADO"])

        jogos_avaliados = []

        for _ in range(candidatos):
            dezenas = sorted(random.sample(range(1, 26), 15))
            repeticoes = len(set(dezenas) & dezenas_ultimo)

            score = ProbabilisticEngine.calcular_score(
                dezenas,
                repeticoes,
                config
            )

            if repeticoes <= config["max_repeticoes"]:
                jogo = Concurso(
                    numero=0,
                    data="",
                    dezenas=tuple(dezenas)
                )
                jogos_avaliados.append((jogo, score, repeticoes))

        jogos_ordenados = sorted(
            jogos_avaliados,
            key=lambda x: x[1],
            reverse=True
        )

        return jogos_ordenados[:quantidade]

    @staticmethod
    def calcular_score(
        dezenas: List[int],
        repeticoes: int,
        config: dict
    ) -> float:

        score_base = sum(dezenas) / 100

        penalizacao = repeticoes * config["penalizacao"]

        score_final = (
            score_base * config["peso_recencia"]
            - penalizacao
        )

        return score_final