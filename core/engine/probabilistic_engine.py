# core/engine/probabilistic_engine.py

import random
from typing import List, Tuple

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10


class ProbabilisticEngine:
    """
    Motor probabilístico de geração de jogos.

    Fluxo:
        - Usa o histórico completo de concursos como base.
        - Gera candidatos aleatórios respeitando o tamanho do jogo (15 dezenas).
        - Controla o número máximo de repetições em relação ao último concurso.
        - Calcula um score estrutural adaptativo (V10) para cada jogo.
        - Retorna apenas os melhores jogos segundo o score.

    Modos disponíveis:
        - CONSERVADOR
        - BALANCEADO
        - AGRESSIVO

    Os modos controlam apenas os limites de repetição e filtro externo;
    o score interno (V10) já é adaptativo ao ciclo do histórico.
    """

    @staticmethod
    def gerar_jogos(
        concursos: List[Concurso],
        quantidade: int = 5,
        candidatos: int = 300,
        modo: str = "BALANCEADO",
    ) -> List[Tuple[Concurso, float, int]]:
        """
        Gera jogos avaliados pelo score V10.

        Args:
            concursos: Lista de concursos históricos (mais antigos primeiro).
            quantidade: Quantos jogos finais retornar.
            candidatos: Quantos candidatos gerar antes do filtro por score.
            modo: Modo estratégico ("CONSERVADOR", "BALANCEADO", "AGRESSIVO").

        Returns:
            Lista de tuplas (jogo, score, repeticoes) ordenada por score desc.
        """
        if not concursos:
            raise ValueError("Lista de concursos não pode ser vazia.")

        ultimo_concurso = concursos[-1]
        dezenas_ultimo = set(ultimo_concurso.dezenas)

        configuracoes = {
            "CONSERVADOR": {
                "max_repeticoes": 9,
            },
            "BALANCEADO": {
                "max_repeticoes": 11,
            },
            "AGRESSIVO": {
                "max_repeticoes": 13,
            },
        }

        config = configuracoes.get(modo.upper(), configuracoes["BALANCEADO"])
        max_repeticoes = config["max_repeticoes"]

        jogos_avaliados: List[Tuple[Concurso, float, int]] = []

        for _ in range(candidatos):
            dezenas = sorted(random.sample(range(1, 26), 15))
            repeticoes = len(set(dezenas) & dezenas_ultimo)

            # Aplica filtro de repetição por modo (mesmo comportamento de antes)
            if repeticoes > max_repeticoes:
                continue

            jogo = Concurso(
                numero=0,
                data="",
                dezenas=tuple(dezenas),
            )

            # Calcula o score V10 usando todo o histórico
            resultado_v10 = calcular_score_v10(jogo, concursos)
            score = resultado_v10.score_final

            jogos_avaliados.append((jogo, score, repeticoes))

        jogos_ordenados = sorted(
            jogos_avaliados,
            key=lambda x: x[1],
            reverse=True,
        )

        return jogos_ordenados[:quantidade]