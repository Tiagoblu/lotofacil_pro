import statistics
from collections import Counter
from pathlib import Path

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.domain.models import Concurso

# Importa o motor V9 atual (ajuste o caminho se o nome/estrutura for diferente)
from rodar_backtest_v9_v10 import gerar_jogos_v9  # reaproveitando a função que você já tem


def analisar_jogos_v9(concursos, quantidade_concursos=200, jogos_por_concurso=10, modo="BALANCEADO"):
    """
    Gera jogos com o V9 ao longo dos últimos N concursos
    e calcula estatísticas agregadas sobre o perfil dos jogos.
    """
    concursos_teste = concursos[-quantidade_concursos:]
    estatisticas = {
        "somas": [],
        "pares": [],
        "impares": [],
        "faixas": [],          # lista de tuplas (q1, q2, q3, q4, q5)
        "repeticoes": [],      # repetição com o último concurso
    }

    for i in range(len(concursos_teste)):
        historico = concursos[:len(concursos) - quantidade_concursos + i]
        if not historico:
            continue

        concurso_real = concursos_teste[i]
        ultimo_concurso = historico[-1]
        dezenas_ultimo = set(ultimo_concurso.dezenas)

        jogos = gerar_jogos_v9(historico, quantidade=jogos_por_concurso, modo=modo)

        for jogo, score, repeticoes in jogos:
            dezenas = list(jogo.dezenas)

            soma = sum(dezenas)
            pares = sum(1 for d in dezenas if d % 2 == 0)
            impares = 15 - pares

            q1 = sum(1 for d in dezenas if 1 <= d <= 5)
            q2 = sum(1 for d in dezenas if 6 <= d <= 10)
            q3 = sum(1 for d in dezenas if 11 <= d <= 15)
            q4 = sum(1 for d in dezenas if 16 <= d <= 20)
            q5 = sum(1 for d in dezenas if 21 <= d <= 25)

            # Repetições com o último concurso disponível naquele momento
            rep_ultimo = len(set(dezenas) & dezenas_ultimo)

            estatisticas["somas"].append(soma)
            estatisticas["pares"].append(pares)
            estatisticas["impares"].append(impares)
            estatisticas["faixas"].append((q1, q2, q3, q4, q5))
            estatisticas["repeticoes"].append(rep_ultimo)

    return estatisticas


def resumir_estatisticas(est):
    print("===== PERFIL DOS JOGOS GERADOS PELO MOTOR V9 =====\n")

    somas = est["somas"]
    pares = est["pares"]
    impares = est["impares"]
    faixas = est["faixas"]
    repeticoes = est["repeticoes"]

    total_jogos = len(somas)
    if total_jogos == 0:
        print("Nenhum jogo gerado para análise.")
        return

    print(f"Total de jogos analisados: {total_jogos}\n")

    # Soma
    print("SOMA DAS DEZENAS:")
    print(f"  Média:  {statistics.mean(somas):.2f}")
    print(f"  Mínima: {min(somas)}")
    print(f"  Máxima: {max(somas)}\n")

    # Pares / Ímpares
    print("PARES / ÍMPARES:")
    print(f"  Pares   - média: {statistics.mean(pares):.2f}")
    print(f"  Ímpares - média: {statistics.mean(impares):.2f}")

    dist_pares = Counter(pares)
    print("  Distribuição de pares (valor: frequência %):")
    for v in sorted(dist_pares):
        perc = dist_pares[v] / total_jogos * 100
        print(f"    {v:2d} pares: {perc:5.1f}%")
    print()

    # Faixas
    print("DISTRIBUIÇÃO POR FAIXAS (1-5, 6-10, 11-15, 16-20, 21-25):")
    medias_faixas = [statistics.mean([f[i] for f in faixas]) for i in range(5)]
    print(f"  Médias por faixa: {', '.join(f'{m:.2f}' for m in medias_faixas)}")
    print()

    # Repetições com o último concurso
    print("REPETIÇÃO COM O ÚLTIMO CONCURSO (no momento da geração):")
    print(f"  Média: {statistics.mean(repeticoes):.2f}")
    dist_rep = Counter(repeticoes)
    print("  Distribuição (repetições: frequência %):")
    for v in sorted(dist_rep):
        perc = dist_rep[v] / total_jogos * 100
        print(f"    {v:2d} dezenas repetidas: {perc:5.1f}%")
    print()


def main():
    print("==== LotoFácil Pro – Análise do Motor V9 ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos disponíveis: {len(concursos)}\n")

    modo = "BALANCEADO"
    quantidade_concursos = 200
    jogos_por_concurso = 10

    print(f"Modo               : {modo}")
    print(f"Concursos analisados: {quantidade_concursos}")
    print(f"Jogos por concurso : {jogos_por_concurso}")
    print()

    estatisticas = analisar_jogos_v9(
        concursos,
        quantidade_concursos=quantidade_concursos,
        jogos_por_concurso=jogos_por_concurso,
        modo=modo,
    )

    resumir_estatisticas(estatisticas)


if __name__ == "__main__":
    main()