# core/engine/probabilistic_engine.py

import random
from typing import Dict, List, Tuple, Any

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10
from core.statistics.score_v10 import detectar_ciclo


class ProbabilisticEngine:
    """
    Motor probabilístico de geração de jogos.

    Fluxo:
        - Detecta o ciclo atual do histórico via score_v10.detectar_ciclo().
        - Gera candidatos aleatórios com 15 dezenas.
        - Filtra candidatos pelo limite de repetições do modo escolhido.
        - Calcula o score V10 para cada candidato.
        - Retorna os melhores jogos ordenados por score.

    Modos disponíveis:
        - CONSERVADOR : max 7 repetições em relação ao último concurso
        - BALANCEADO  : max 8 repetições  ← reduzido de 11 para forçar alvo 7-8
        - AGRESSIVO   : max 9 repetições  ← reduzido de 13
    """

    @staticmethod
    def gerar_jogos(
        concursos: List[Concurso],
        quantidade: int = 5,
        candidatos: int = 300,
        modo: str = "BALANCEADO"
    ) -> Tuple[List[Tuple[Concurso, float, int]], Dict[str, Any]]:
        """
        Gera jogos avaliados pelo score V10.

        Args:
            concursos:  Lista de concursos históricos (mais antigos primeiro).
            quantidade: Quantos jogos finais retornar.
            candidatos: Quantos candidatos gerar antes do filtro por score.
            modo:       Modo estratégico ("CONSERVADOR", "BALANCEADO", "AGRESSIVO").

        Returns:
            Tupla com:
                - Lista de (jogo, score, repeticoes) ordenada por score desc.
                - Dicionário com informações do ciclo detectado pelo V10:
                    {ciclo, indice_volatilidade, peso_recencia}
        """
        if not concursos:
            raise ValueError("Lista de concursos não pode ser vazia.")

        # Detecta o ciclo uma única vez para todo o lote
        resultado_ciclo = detectar_ciclo(concursos)

        info_ciclo: Dict[str, Any] = {
            "ciclo"               : resultado_ciclo.ciclo,
            "indice_volatilidade" : resultado_ciclo.indice_volatilidade,
            "peso_recencia"       : resultado_ciclo.peso_recencia,
        }

        ultimo_concurso = concursos[-1]
        dezenas_ultimo  = set(ultimo_concurso.dezenas)

        # max_repeticoes reduzido para forçar jogos no alvo 7-8
        configuracoes = {
            "CONSERVADOR": {"max_repeticoes": 7},
            "BALANCEADO" : {"max_repeticoes": 8},
            "AGRESSIVO"  : {"max_repeticoes": 9},
        }

        config         = configuracoes.get(modo.upper(), configuracoes["BALANCEADO"])
        max_repeticoes = config["max_repeticoes"]

        jogos_avaliados: List[Tuple[Concurso, float, int]] = []

        for _ in range(candidatos):
            dezenas    = sorted(random.sample(range(1, 26), 15))
            repeticoes = len(set(dezenas) & dezenas_ultimo)

            if repeticoes > max_repeticoes:
                continue

            jogo = Concurso(
                numero=0,
                data="",
                dezenas=tuple(dezenas)
            )

            resultado_v10 = calcular_score_v10(jogo, concursos)
            score         = resultado_v10.score_final

            jogos_avaliados.append((jogo, score, repeticoes))

        jogos_ordenados = sorted(
            jogos_avaliados,
            key=lambda x: x[1],
            reverse=True
        )

        return jogos_ordenados[:quantidade], info_ciclo