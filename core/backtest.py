from core.metricas import (
    frequencia_total,
    frequencia_recente,
    atraso_dezenas,
)
from core.scoring import calcular_score
from core.database import obter_todos_concursos
import random


def carregar_historico_completo():
    dados = obter_todos_concursos()
    historico = []

    for linha in dados:
        if not linha or not linha[0]:
            continue

        dezenas_str = linha[0].replace(",", " ").split()

        try:
            dezenas = sorted([int(d) for d in dezenas_str])
            historico.append(dezenas)
        except ValueError:
            continue

    return historico


def rodar_backtest(
    janela_minima=200,
    jogos_por_concurso=5,
    simulacoes=2000
):
    """
    Backtest Walk-Forward:
    Usa histórico progressivo e testa contra concurso seguinte.
    """

    historico = carregar_historico_completo()

    if len(historico) <= janela_minima:
        return {"erro": "Histórico insuficiente"}

    total_11 = 0
    total_12 = 0
    total_13 = 0
    total_testes = 0

    for i in range(janela_minima, len(historico) - 1):

        base = historico[:i]
        resultado_real = historico[i]

        freq_total = frequencia_total(base)
        freq_recente = frequencia_recente(base)
        atraso = atraso_dezenas(base)

        jogos = []

        for _ in range(simulacoes):
            jogo = sorted(random.sample(range(1, 26), 15))
            score = calcular_score(jogo, freq_total, freq_recente, atraso)
            jogos.append((jogo, score))

        jogos.sort(key=lambda x: x[1], reverse=True)
        melhores = [j[0] for j in jogos[:jogos_por_concurso]]

        for jogo in melhores:
            acertos = len(set(jogo) & set(resultado_real))

            if acertos == 11:
                total_11 += 1
            elif acertos == 12:
                total_12 += 1
            elif acertos >= 13:
                total_13 += 1

        total_testes += 1

    return {
        "concursos_testados": total_testes,
        "acertos_11": total_11,
        "acertos_12": total_12,
        "acertos_13_ou_mais": total_13,
        "media_11": total_11 / total_testes,
        "media_12": total_12 / total_testes,
        "media_13+": total_13 / total_testes,
    }