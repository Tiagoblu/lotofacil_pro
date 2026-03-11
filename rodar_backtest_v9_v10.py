# rodar_backtest_v9_v10.py

import random
import statistics
import sqlite3
from pathlib import Path

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10


DB_PATH = Path("database/lotofacil.db")


# ==========================================
# MOTOR V9 (score simplificado original)
# ==========================================

def gerar_jogos_v9(
    concursos,
    quantidade=10,
    candidatos=300,
    modo="BALANCEADO"
):
    configuracoes = {
        "CONSERVADOR": {
            "max_repeticoes": 9,
            "peso_recencia": 0.55,
            "penalizacao": 0.15
        },
        "BALANCEADO": {
            "max_repeticoes": 11,
            "peso_recencia": 0.65,
            "penalizacao": 0.10
        },
        "AGRESSIVO": {
            "max_repeticoes": 13,
            "peso_recencia": 0.75,
            "penalizacao": 0.05
        }
    }

    config = configuracoes.get(modo.upper(), configuracoes["BALANCEADO"])
    ultimo_concurso = concursos[-1]
    dezenas_ultimo = set(ultimo_concurso.dezenas)

    jogos_avaliados = []

    for _ in range(candidatos):
        dezenas = sorted(random.sample(range(1, 26), 15))
        repeticoes = len(set(dezenas) & dezenas_ultimo)

        if repeticoes > config["max_repeticoes"]:
            continue

        score_base = sum(dezenas) / 100
        penalizacao = repeticoes * config["penalizacao"]
        score_final = score_base * config["peso_recencia"] - penalizacao

        jogo = Concurso(numero=0, data="", dezenas=tuple(dezenas))
        jogos_avaliados.append((jogo, score_final, repeticoes))

    jogos_ordenados = sorted(
        jogos_avaliados,
        key=lambda x: x[1],
        reverse=True
    )

    return jogos_ordenados[:quantidade]


# ==========================================
# MOTOR V10 (score estrutural adaptativo)
# ==========================================

def gerar_jogos_v10(
    concursos,
    quantidade=10,
    candidatos=300,
    modo="BALANCEADO"
):
    configuracoes = {
        "CONSERVADOR": {"max_repeticoes": 9},
        "BALANCEADO":  {"max_repeticoes": 11},
        "AGRESSIVO":   {"max_repeticoes": 13},
    }

    config = configuracoes.get(modo.upper(), configuracoes["BALANCEADO"])
    ultimo_concurso = concursos[-1]
    dezenas_ultimo = set(ultimo_concurso.dezenas)

    jogos_avaliados = []

    for _ in range(candidatos):
        dezenas = sorted(random.sample(range(1, 26), 15))
        repeticoes = len(set(dezenas) & dezenas_ultimo)

        if repeticoes > config["max_repeticoes"]:
            continue

        jogo = Concurso(numero=0, data="", dezenas=tuple(dezenas))
        resultado_v10 = calcular_score_v10(jogo, concursos)
        score = resultado_v10.score_final

        jogos_avaliados.append((jogo, score, repeticoes))

    jogos_ordenados = sorted(
        jogos_avaliados,
        key=lambda x: x[1],
        reverse=True
    )

    return jogos_ordenados[:quantidade]


# ==========================================
# BACKTEST GENÉRICO
# ==========================================

def executar_backtest(concursos, motor_fn, quantidade_concursos=200, jogos_por_concurso=10, modo="BALANCEADO"):
    concursos_teste = concursos[-quantidade_concursos:]
    resultados = []

    for i in range(len(concursos_teste)):
        historico = concursos[:len(concursos) - quantidade_concursos + i]
        concurso_real = concursos_teste[i]

        if not historico:
            continue

        jogos = motor_fn(historico, quantidade=jogos_por_concurso, modo=modo)

        for jogo, score, repeticoes in jogos:
            acertos = len(set(jogo.dezenas) & set(concurso_real.dezenas))
            resultados.append(acertos)

    return resultados


def calcular_metricas(resultados, nome):
    total = len(resultados)
    if total == 0:
        print(f"{nome}: sem resultados.")
        return

    media = statistics.mean(resultados)
    desvio = statistics.pstdev(resultados)
    melhor = max(resultados)

    p11 = sum(1 for r in resultados if r >= 11) / total * 100
    p12 = sum(1 for r in resultados if r >= 12) / total * 100
    p13 = sum(1 for r in resultados if r >= 13) / total * 100
    p14 = sum(1 for r in resultados if r >= 14) / total * 100

    print(f"Motor       : {nome}")
    print(f"Total jogos : {total}")
    print(f"Média       : {media:.3f}")
    print(f"Desvio      : {desvio:.3f}")
    print(f"Melhor      : {melhor}")
    print(f"% 11+       : {p11:.1f}%")
    print(f"% 12+       : {p12:.1f}%")
    print(f"% 13+       : {p13:.1f}%")
    print(f"% 14+       : {p14:.1f}%")
    print("-" * 50)


# ==========================================
# MAIN
# ==========================================

def main():
    print("==== LotoFácil Pro – Backtest Comparativo V9 x V10 ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos disponíveis: {len(concursos)}\n")

    modo = "BALANCEADO"
    quantidade_concursos = 200
    jogos_por_concurso = 10

    print(f"Modo         : {modo}")
    print(f"Concursos    : {quantidade_concursos}")
    print(f"Jogos/conc.  : {jogos_por_concurso}")
    print(f"Total jogos  : {quantidade_concursos * jogos_por_concurso}")
    print()

    print("Rodando V9...")
    resultados_v9 = executar_backtest(
        concursos,
        motor_fn=gerar_jogos_v9,
        quantidade_concursos=quantidade_concursos,
        jogos_por_concurso=jogos_por_concurso,
        modo=modo
    )

    print("Rodando V10...")
    resultados_v10 = executar_backtest(
        concursos,
        motor_fn=gerar_jogos_v10,
        quantidade_concursos=quantidade_concursos,
        jogos_por_concurso=jogos_por_concurso,
        modo=modo
    )

    print("\n===== RESULTADO COMPARATIVO V9 x V10 =====\n")
    calcular_metricas(resultados_v9, "V9 (score simplificado)")
    calcular_metricas(resultados_v10, "V10 (score estrutural adaptativo)")

    # Diferença
    if resultados_v9 and resultados_v10:
        media_v9 = statistics.mean(resultados_v9)
        media_v10 = statistics.mean(resultados_v10)
        diff = media_v10 - media_v9
        sinal = "+" if diff >= 0 else ""
        print(f"Diferença de média V10 - V9: {sinal}{diff:.3f}")


if __name__ == "__main__":
    main()