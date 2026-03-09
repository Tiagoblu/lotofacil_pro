import csv
import statistics
from core.engine.probabilistic_engine import ProbabilisticEngine


class BacktestEngine:

    @staticmethod
    def executar(concursos, quantidade_concursos=100, jogos_por_concurso=10):

        resultados = []

        concursos_teste = concursos[-quantidade_concursos:]

        print(f"Executando backtest ({quantidade_concursos} concursos / {jogos_por_concurso} jogos por concurso)...\n")

        for i in range(len(concursos_teste)):

            historico = concursos[:len(concursos) - quantidade_concursos + i]
            concurso_real = concursos_teste[i]

            jogos_motor = ProbabilisticEngine.gerar_jogos(
                historico,
                quantidade=jogos_por_concurso,
                candidatos=300
            )

            for jogo, score, repeticoes in jogos_motor:
                acertos = len(set(jogo.dezenas) & set(concurso_real.dezenas))
                resultados.append(acertos)

        total_jogos = len(resultados)
        media = statistics.mean(resultados)
        desvio = statistics.pstdev(resultados)

        acima_11 = sum(1 for r in resultados if r >= 11)
        acima_12 = sum(1 for r in resultados if r >= 12)
        acima_13 = sum(1 for r in resultados if r >= 13)

        resumo = {
            "total_jogos": total_jogos,
            "media": round(media, 3),
            "melhor": max(resultados),
            "desvio": round(desvio, 3),
            "11+": round((acima_11 / total_jogos) * 100, 1),
            "12+": round((acima_12 / total_jogos) * 100, 1),
            "13+": round((acima_13 / total_jogos) * 100, 1),
        }

        with open("backtest_resultados.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Acertos"])
            for r in resultados:
                writer.writerow([r])

        return resultados, resumo