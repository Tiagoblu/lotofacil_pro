# core/avaliacao/backtest_engine.py

import csv
import statistics

from core.engine.probabilistic_engine import ProbabilisticEngine
from core.ia.analise_inteligente import AnaliseInteligente


class BacktestEngine:

    @staticmethod
    def executar(concursos, quantidade_concursos=100, jogos_por_concurso=10):

        if len(concursos) <= quantidade_concursos:
            raise ValueError("Quantidade de concursos insuficiente para backtest.")

        resultados_concurso = []

        inicio = len(concursos) - quantidade_concursos

        for i in range(inicio, len(concursos)):

            concurso_teste = concursos[i]
            historico = concursos[:i]

            # 1️⃣ Gerar jogos usando motor real
            jogos_motor = ProbabilisticEngine.gerar_jogos(
                historico,
                quantidade=jogos_por_concurso
            )

            # Converter para formato esperado pela IA
            jogos_formatados = [
                (tuple(jogo.dezenas), score)
                for jogo, score in jogos_motor
            ]

            # 2️⃣ Aplicar Análise Inteligente
            analise = AnaliseInteligente.analisar(jogos_formatados, historico)

            # 3️⃣ Comparar com resultado real
            resultado_real = set(concurso_teste.dezenas)

            acertos_lista = []

            for item in analise:
                jogo = set(item["jogo"])
                acertos = len(jogo & resultado_real)
                acertos_lista.append(acertos)

            melhor_acerto = max(acertos_lista)
            media_acertos = round(statistics.mean(acertos_lista), 2)

            jogos_11 = sum(1 for a in acertos_lista if a >= 11)
            jogos_12 = sum(1 for a in acertos_lista if a >= 12)
            jogos_13 = sum(1 for a in acertos_lista if a >= 13)

            resultados_concurso.append({
                "numero_concurso": concurso_teste.numero,
                "melhor_acerto": melhor_acerto,
                "media_acertos": media_acertos,
                "jogos_11_mais": jogos_11,
                "jogos_12_mais": jogos_12,
                "jogos_13_mais": jogos_13
            })

        # 📊 Consolidação geral
        todas_medias = [r["media_acertos"] for r in resultados_concurso]
        todos_melhores = [r["melhor_acerto"] for r in resultados_concurso]

        media_geral = round(statistics.mean(todas_medias), 3)
        melhor_geral = max(todos_melhores)
        desvio_padrao = round(statistics.stdev(todas_medias), 3)

        total_jogos = quantidade_concursos * jogos_por_concurso
        total_11 = sum(r["jogos_11_mais"] for r in resultados_concurso)
        total_12 = sum(r["jogos_12_mais"] for r in resultados_concurso)
        total_13 = sum(r["jogos_13_mais"] for r in resultados_concurso)

        percentual_11 = round((total_11 / total_jogos) * 100, 2)
        percentual_12 = round((total_12 / total_jogos) * 100, 2)
        percentual_13 = round((total_13 / total_jogos) * 100, 2)

        resumo = {
            "media_geral": media_geral,
            "melhor_resultado": melhor_geral,
            "desvio_padrao": desvio_padrao,
            "percentual_11+": percentual_11,
            "percentual_12+": percentual_12,
            "percentual_13+": percentual_13,
            "total_jogos_testados": total_jogos
        }

        return resultados_concurso, resumo

    @staticmethod
    def exportar_csv(resultados, nome_arquivo="backtest_resultados.csv"):

        with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)