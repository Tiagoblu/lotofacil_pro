# rodar_backtest.py

from infrastructure.database.repository import ConcursoRepository
from core.avaliacao.backtest_engine import BacktestEngine


def main():

    print("==== LotoFácil Pro - Backtest V1 ====\n")

    concursos = ConcursoRepository.obter_todos()

    print(f"Total de concursos disponíveis: {len(concursos)}\n")

    print("Executando backtest (100 concursos / 10 jogos por concurso)...\n")

    resultados, resumo = BacktestEngine.executar(
        concursos,
        quantidade_concursos=100,
        jogos_por_concurso=10
    )

    BacktestEngine.exportar_csv(resultados)

    print("===== RESUMO FINAL =====\n")

    print(f"Total de jogos testados: {resumo['total_jogos_testados']}")
    print(f"Média geral de acertos: {resumo['media_geral']}")
    print(f"Melhor resultado obtido: {resumo['melhor_resultado']}")
    print(f"Desvio padrão das médias: {resumo['desvio_padrao']}")
    print(f"% Jogos com 11+: {resumo['percentual_11+']}%")
    print(f"% Jogos com 12+: {resumo['percentual_12+']}%")
    print(f"% Jogos com 13+: {resumo['percentual_13+']}%")

    print("\nArquivo CSV gerado: backtest_resultados.csv")


if __name__ == "__main__":
    main()