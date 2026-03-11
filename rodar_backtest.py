# rodar_backtest.py

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.avaliacao.backtest_engine import BacktestEngine


def main():
    print("==== LotoFácil Pro V10 - Backtest Comparativo ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos disponíveis: {len(concursos)}\n")

    modos = ["CONSERVADOR", "BALANCEADO", "AGRESSIVO"]
    resultados_por_modo = {}

    for modo in modos:
        print(f"Rodando modo: {modo}...")
        resultados, resumo = BacktestEngine.executar(
            concursos,
            quantidade_concursos=200,
            jogos_por_concurso=10,
            candidatos_por_concurso=300,
            modo=modo,
            salvar_csv=True,
            caminho_csv=f"backtest_{modo.lower()}.csv",
        )
        resultados_por_modo[modo] = resumo

    print("\n===== RESULTADO COMPARATIVO =====\n")

    for modo, resumo in resultados_por_modo.items():
        print(f"Modo: {modo}")
        print(f"Média de acertos: {resumo['media']}")
        print(f"Desvio padrão: {resumo['desvio']}")
        print(f"% 11+: {resumo['11+']}%")
        print(f"% 12+: {resumo['12+']}%")
        print(f"% 13+: {resumo['13+']}%")
        print(f"% 14+: {resumo['14+']}%")
        print(f"Melhor resultado: {resumo['melhor']}")
        print(f"Total de jogos testados: {resumo['total_jogos']}")
        print("-" * 50)


if __name__ == "__main__":
    main()