# backtest_v10.py
"""
Backtest do Motor V10 usando o mesmo estilo de lógica do V9.

Fluxo:
  - Para cada concurso de teste:
      * Usa todo o histórico anterior como contexto
      * Gera N jogos com o ProbabilisticEngine (modo configurável)
      * Compara com o resultado real daquele concurso
      * Registra o melhor número de acertos (15..0)
  - Ao final:
      * Mostra média de acertos por jogo
      * Distribuição do "melhor jogo" por concurso (15, 14, 13, 12, 11...)
      * Percentual de concursos em que houve jogo com 11+ pontos

Uso típico (espelhando V9):
    py backtest_v10.py --concursos 500 --jogos 10 --modo BALANCEADO
"""

import sys
import os
import argparse
from collections import Counter

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine


ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def contar_acertos(jogo_dezenas, resultado_dezenas):
    """Conta quantas dezenas o jogo acertou no resultado."""
    return len(set(jogo_dezenas) & set(resultado_dezenas))


def backtest_v10(
    qtd_concursos: int = 500,
    modo: str = "BALANCEADO",
    jogos_por_concurso: int = 10,
    candidatos: int = 300,
):
    """
    Executa o backtest do Motor V10.

    Args:
        qtd_concursos:      Quantos concursos reais usar no teste (do fim para trás).
        modo:               Modo do motor (CONSERVADOR/BALANCEADO/AGRESSIVO).
        jogos_por_concurso: Quantos jogos gerar para cada concurso (espelhar V9).
        candidatos:         Quantos candidatos gerar no motor antes do filtro por score.
    """
    inicializar_banco()
    concursos = ConcursoRepository.obter_todos()

    if len(concursos) <= qtd_concursos:
        raise ValueError(
            f"Banco tem poucos concursos ({len(concursos)}). "
            f"Reduza --concursos ou atualize o banco."
        )

    # Seleciona os últimos N concursos para teste (mais recentes)
    concursos_teste = concursos[-qtd_concursos:]

    dist_melhor = Counter()   # melhor resultado por concurso
    soma_pontos = 0
    total_jogos = 0

    print(f"\nIniciando backtest V10...")
    print(f"  Concursos de teste     : {qtd_concursos}")
    print(f"  Modo do motor          : {modo}")
    print(f"  Jogos por concurso     : {jogos_por_concurso}")
    print(f"  Candidatos por concurso: {candidatos}")
    print("-" * 60)

    for idx, concurso in enumerate(concursos_teste, 1):
        # Histórico até o concurso anterior (igual fazíamos no V9)
        historico = [c for c in concursos if c.numero < concurso.numero]
        if not historico:
            continue

        # Gera jogos com o Motor V10 usando apenas o histórico passado
        jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
            historico,
            quantidade=jogos_por_concurso,
            candidatos=candidatos,
            modo=modo,
        )

        resultado = set(concurso.dezenas)

        melhor = 0
        for jogo_obj, score, repet in jogos_motor:
            acertos = contar_acertos(jogo_obj.dezenas, resultado)
            melhor = max(melhor, acertos)
            soma_pontos += acertos
            total_jogos += 1

        dist_melhor[melhor] += 1

        print(
            f"[{idx:3d}/{qtd_concursos}] Concurso {concurso.numero} | "
            f"melhor jogo: {melhor:2d} pontos | "
            f"ciclo: {info_ciclo['ciclo']}"
        )

    print("\n===== RESUMO BACKTEST V10 =====")
    total_conc = sum(dist_melhor.values())
    print(f"Concursos testados       : {total_conc}")
    print(f"Jogos gerados (total)    : {total_jogos}")

    media_por_jogo = soma_pontos / total_jogos if total_jogos > 0 else 0.0
    print(f"Média de pontos por jogo : {media_por_jogo:.3f}\n")

    print("Melhor resultado por concurso (distribuição):")
    for pontos in sorted(dist_melhor.keys(), reverse=True):
        qtd = dist_melhor[pontos]
        print(f"  {pontos:2d} pontos: {qtd:4d}")

    # % concursos com 11+ no melhor jogo
    conc_11_mais = sum(qtd for pontos, qtd in dist_melhor.items() if pontos >= 11)
    perc_11_mais = conc_11_mais / total_conc * 100 if total_conc > 0 else 0.0
    print(
        f"\nConcursos com melhor jogo >= 11 pontos: "
        f"{conc_11_mais} ({perc_11_mais:.2f}%)"
    )

    return dist_melhor, media_por_jogo, perc_11_mais


def parse_args():
    parser = argparse.ArgumentParser(description="Backtest do Motor V10")
    parser.add_argument(
        "--concursos",
        type=int,
        default=500,
        help="quantidade de concursos reais a testar (mais recentes)",
    )
    parser.add_argument(
        "--modo",
        choices=["CONSERVADOR", "BALANCEADO", "AGRESSIVO"],
        default="BALANCEADO",
        help="modo de operação do motor V10",
    )
    parser.add_argument(
        "--jogos",
        type=int,
        default=10,  # espelhando backtest do V9
        help="quantidade de jogos por concurso",
    )
    parser.add_argument(
        "--candidatos",
        type=int,
        default=300,
        help="candidatos gerados por concurso no motor",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    backtest_v10(
        qtd_concursos=args.concursos,
        modo=args.modo,
        jogos_por_concurso=args.jogos,
        candidatos=args.candidatos,
    )


if __name__ == "__main__":
    main()