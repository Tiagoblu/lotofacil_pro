from core.database import obter_todos_concursos
from core.avaliacao.backtest_engine import BacktestEngine


def main():
    print("==== LotoFácil Pro - Backtest V1 ====\n")

    concursos = obter_todos_concursos()
    print(f"Total de concursos disponíveis: {len(concursos)}\n")

    resultados, resumo = BacktestEngine.executar(
        concursos,
        quantidade_concursos=100,
        jogos_por_concurso=10
    )

    print("\n===== RESUMO FINAL =====\n")
    print(f"Total de jogos testados: {resumo['total_jogos']}")
    print(f"Média geral de acertos: {resumo['media']}")
    print(f"Melhor resultado obtido: {resumo['melhor']}")
    print(f"Desvio padrão: {resumo['desvio']}")
    print(f"% Jogos com 11+: {resumo['11+']}%")
    print(f"% Jogos com 12+: {resumo['12+']}%")
    print(f"% Jogos com 13+: {resumo['13+']}%")
    print("\nArquivo CSV gerado: backtest_resultados.csv")


if __name__ == "__main__":
    main()