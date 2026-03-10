# rodar_backtest.py

from statistics import mean, pstdev
from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine


def calcular_acertos(jogo_dezenas, concurso_dezenas):
    return len(set(jogo_dezenas) & set(concurso_dezenas))


def executar_backtest(modo, concursos, quantidade_concursos=200, jogos_por_concurso=10):
    resultados = []

    concursos_teste = concursos[-quantidade_concursos:]

    for i in range(len(concursos_teste) - 1):
        historico = concursos[: -(quantidade_concursos - i)]
        concurso_real = concursos_teste[i + 1]

        jogos = ProbabilisticEngine.gerar_jogos(
            historico,
            quantidade=jogos_por_concurso,
            candidatos=300,
            modo=modo
        )

        for jogo, score, repeticoes in jogos:
            acertos = calcular_acertos(jogo.dezenas, concurso_real.dezenas)
            resultados.append(acertos)

    media = mean(resultados)
    desvio = pstdev(resultados)
    total = len(resultados)

    faixa_11 = sum(1 for r in resultados if r >= 11) / total * 100
    faixa_12 = sum(1 for r in resultados if r >= 12) / total * 100
    faixa_13 = sum(1 for r in resultados if r >= 13) / total * 100
    faixa_14 = sum(1 for r in resultados if r >= 14) / total * 100

    melhor = max(resultados)

    return {
        "modo": modo,
        "media": media,
        "desvio": desvio,
        "11+": faixa_11,
        "12+": faixa_12,
        "13+": faixa_13,
        "14+": faixa_14,
        "melhor": melhor,
        "total": total
    }


def main():
    print("==== LotoFácil Pro - Backtest Comparativo ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos disponíveis: {len(concursos)}\n")

    modos = ["CONSERVADOR", "BALANCEADO", "AGRESSIVO"]

    print("Executando backtest (200 concursos / 10 jogos por concurso)...\n")

    resultados_finais = []

    for modo in modos:
        print(f"Rodando modo: {modo}...")
        resultado = executar_backtest(modo, concursos)
        resultados_finais.append(resultado)

    print("\n===== RESULTADO COMPARATIVO =====\n")

    for r in resultados_finais:
        print(f"Modo: {r['modo']}")
        print(f"Média de acertos: {r['media']:.3f}")
        print(f"Desvio padrão: {r['desvio']:.3f}")
        print(f"% 11+: {r['11+']:.2f}%")
        print(f"% 12+: {r['12+']:.2f}%")
        print(f"% 13+: {r['13+']:.2f}%")
        print(f"% 14+: {r['14+']:.2f}%")
        print(f"Melhor resultado: {r['melhor']}")
        print(f"Total de jogos testados: {r['total']}")
        print("-" * 50)


if __name__ == "__main__":
    main()