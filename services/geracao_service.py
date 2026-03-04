# services/geracao_service.py

from infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine


class GeracaoService:

    @staticmethod
    def gerar_jogos(quantidade=10, candidatos=500):
        concursos = ConcursoRepository.obter_todos()

        if not concursos:
            return []

        jogos = ProbabilisticEngine.gerar_jogos(
            concursos=concursos,
            quantidade=quantidade,
            candidatos=candidatos
        )

        # Converte para formato simples (tuple + score)
        return [
            (tuple(jogo.dezenas), score)
            for jogo, score in jogos
        ]