import csv
import logging
import statistics
from typing import List, Tuple, Dict, Any

from core.engine.probabilistic_engine import ProbabilisticEngine

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Executa backtests gerando jogos com o ProbabilisticEngine e
    medindo a distribuição de acertos em concursos históricos.

    Estratégia:
        - Para os N últimos concursos (janela de teste):
            - Usa apenas o histórico anterior a cada concurso como base
            - Gera K jogos para esse concurso
            - Avalia os acertos de cada jogo contra o resultado real
        - Consolida métricas agregadas ao final.
    """

    @staticmethod
    def _calcular_metricas(resultados: List[int]) -> Dict[str, Any]:
        """Calcula métricas agregadas a partir da lista de acertos."""
        total_jogos = len(resultados)
        media = statistics.mean(resultados) if resultados else 0.0
        desvio = statistics.pstdev(resultados) if len(resultados) > 1 else 0.0

        acima_11 = sum(1 for r in resultados if r >= 11)
        acima_12 = sum(1 for r in resultados if r >= 12)
        acima_13 = sum(1 for r in resultados if r >= 13)

        resumo = {
            "total_jogos": total_jogos,
            "media": round(media, 3),
            "melhor": max(resultados) if resultados else 0,
            "desvio": round(desvio, 3),
            "11+": round((acima_11 / total_jogos) * 100, 1) if total_jogos else 0.0,
            "12+": round((acima_12 / total_jogos) * 100, 1) if total_jogos else 0.0,
            "13+": round((acima_13 / total_jogos) * 100, 1) if total_jogos else 0.0,
        }
        return resumo

    @staticmethod
    def executar(
        concursos: List[Any],
        quantidade_concursos: int = 100,
        jogos_por_concurso: int = 10,
        candidatos_por_concurso: int = 300,
        salvar_csv: bool = True,
        caminho_csv: str = "backtest_resultados.csv",
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Executa o backtest principal.

        Args:
            concursos: Lista de concursos históricos (mais antigos primeiro).
            quantidade_concursos: Quantos concursos finais usar como janela de teste.
            jogos_por_concurso: Quantos jogos gerar para cada concurso de teste.
            candidatos_por_concurso: Número de candidatos gerados pelo motor.
            salvar_csv: Se True, salva os resultados individuais em CSV.
            caminho_csv: Caminho do arquivo CSV de saída.

        Returns:
            (lista_de_acertos, resumo_metricas)
        """
        if not concursos:
            raise ValueError("Lista de concursos não pode ser vazia.")

        if quantidade_concursos <= 0:
            raise ValueError("quantidade_concursos deve ser maior que zero.")

        quantidade_concursos = min(quantidade_concursos, len(concursos))
        concursos_teste = concursos[-quantidade_concursos:]

        logger.info(
            "Executando backtest (%d concursos / %d jogos por concurso / %d candidatos)...",
            quantidade_concursos,
            jogos_por_concurso,
            candidatos_por_concurso,
        )

        resultados: List[int] = []

        for i in range(len(concursos_teste)):
            # histórico: tudo que vem ANTES do concurso que estamos testando
            historico = concursos[: len(concursos) - quantidade_concursos + i]
            concurso_real = concursos_teste[i]

            if not historico:
                # pula caso extremo onde não há histórico anterior suficiente
                logger.warning(
                    "Sem histórico suficiente antes do concurso de teste índice %d. Pulando.",
                    i,
                )
                continue

            jogos_motor = ProbabilisticEngine.gerar_jogos(
                historico,
                quantidade=jogos_por_concurso,
                candidatos=candidatos_por_concurso,
            )

            for jogo, score, repeticoes in jogos_motor:
                acertos = len(set(jogo.dezenas) & set(concurso_real.dezenas))
                resultados.append(acertos)

        resumo = BacktestEngine._calcular_metricas(resultados)

        if salvar_csv:
            with open(caminho_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Acertos"])
                for r in resultados:
                    writer.writerow([r])
            logger.info("Resultados do backtest salvos em '%s'.", caminho_csv)

        logger.info(
            "Backtest concluído: total_jogos=%d, média=%.3f, melhor=%d",
            resumo["total_jogos"],
            resumo["media"],
            resumo["melhor"],
        )

        return resultados, resumo