# core/avaliacao/backtest_engine.py

import csv
import logging
import statistics
from typing import Any, Dict, List, Tuple

from core.engine.probabilistic_engine import ProbabilisticEngine

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Executa backtests gerando jogos com o ProbabilisticEngine (V10)
    e medindo a distribuição de acertos em concursos históricos.
    """

    @staticmethod
    def _calcular_metricas(resultados: List[int]) -> Dict[str, Any]:
        total_jogos = len(resultados)
        if total_jogos == 0:
            return {
                "total_jogos": 0,
                "media": 0.0,
                "melhor": 0,
                "desvio": 0.0,
                "11+": 0.0,
                "12+": 0.0,
                "13+": 0.0,
                "14+": 0.0,
            }

        media = statistics.mean(resultados)
        desvio = statistics.pstdev(resultados)

        acima_11 = sum(1 for r in resultados if r >= 11)
        acima_12 = sum(1 for r in resultados if r >= 12)
        acima_13 = sum(1 for r in resultados if r >= 13)
        acima_14 = sum(1 for r in resultados if r >= 14)

        return {
            "total_jogos": total_jogos,
            "media": round(media, 3),
            "melhor": max(resultados),
            "desvio": round(desvio, 3),
            "11+": round((acima_11 / total_jogos) * 100, 1),
            "12+": round((acima_12 / total_jogos) * 100, 1),
            "13+": round((acima_13 / total_jogos) * 100, 1),
            "14+": round((acima_14 / total_jogos) * 100, 1),
        }

    @staticmethod
    def executar(
        concursos: List[Any],
        quantidade_concursos: int = 200,
        jogos_por_concurso: int = 10,
        candidatos_por_concurso: int = 300,
        modo: str = "BALANCEADO",
        salvar_csv: bool = True,
        caminho_csv: str = "backtest_resultados.csv",
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Executa o backtest com o motor V10.

        Args:
            concursos: Lista de concursos históricos.
            quantidade_concursos: Quantos concursos finais usar como janela de teste.
            jogos_por_concurso: Quantos jogos gerar por concurso.
            candidatos_por_concurso: Candidatos gerados pelo motor antes do filtro.
            modo: Modo estratégico ("CONSERVADOR", "BALANCEADO", "AGRESSIVO").
            salvar_csv: Se True, salva os acertos em CSV.
            caminho_csv: Caminho do arquivo CSV de saída.

        Returns:
            (lista_de_acertos, resumo_metricas)
        """
        if not concursos:
            raise ValueError("Lista de concursos não pode ser vazia.")

        quantidade_concursos = min(quantidade_concursos, len(concursos))
        concursos_teste = concursos[-quantidade_concursos:]

        print(
            f"Executando backtest "
            f"({quantidade_concursos} concursos / "
            f"{jogos_por_concurso} jogos por concurso / "
            f"modo {modo})...\n"
        )

        resultados: List[int] = []

        for i in range(len(concursos_teste)):
            historico = concursos[: len(concursos) - quantidade_concursos + i]
            concurso_real = concursos_teste[i]

            if not historico:
                continue

            # Desempacota a tupla retornada pelo novo ProbabilisticEngine
            jogos_motor, _ = ProbabilisticEngine.gerar_jogos(
                historico,
                quantidade=jogos_por_concurso,
                candidatos=candidatos_por_concurso,
                modo=modo,
            )

            for jogo, score, repeticoes in jogos_motor:
                acertos = len(set(jogo.dezenas) & set(concurso_real.dezenas))
                resultados.append(acertos)

        resumo = BacktestEngine._calcular_metricas(resultados)

        if salvar_csv and resultados:
            with open(caminho_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Acertos"])
                for r in resultados:
                    writer.writerow([r])
            logger.info("Resultados salvos em '%s'.", caminho_csv)

        return resultados, resumo