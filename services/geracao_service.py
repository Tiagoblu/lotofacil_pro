# services/geracao_service.py

import time
from infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine


class GeracaoService:

    @staticmethod
    def gerar_simulacao(
        nivel="C",
        quantidade=10,
        candidatos=1000,
        callback=None
    ):
        """
        Gera jogos usando o motor probabilístico profissional.
        Possui callback de progresso para interface.
        """

        concursos = ConcursoRepository.obter_todos()

        if not concursos:
            return []

        inicio = time.time()

        jogos = ProbabilisticEngine.gerar_jogos(
            concursos=concursos,
            quantidade=quantidade,
            candidatos=candidatos
        )

        resultados = []

        total = len(jogos)

        for i, (jogo, score) in enumerate(jogos):

            progresso = (i + 1) / total
            tempo_decorrido = time.time() - inicio

            if callback:
                callback(progresso, tempo_decorrido)

            resultados.append((tuple(jogo.dezenas), score))

        return resultados

    # Mantemos compatibilidade futura
    @staticmethod
    def gerar_jogos(quantidade=10, candidatos=500):
        return GeracaoService.gerar_simulacao(
            quantidade=quantidade,
            candidatos=candidatos
        )