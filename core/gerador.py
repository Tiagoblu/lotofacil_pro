import random
from core.metricas import (
    carregar_historico,
    frequencia_total,
    frequencia_recente,
    atraso_dezenas,
)
from core.scoring import calcular_score


def gerar_jogos_avancados(quantidade=10, simulacoes=3000):

    historico = carregar_historico()
    freq_total = frequencia_total(historico)
    freq_recente = frequencia_recente(historico)
    atraso = atraso_dezenas(historico)

    jogos = []

    for _ in range(simulacoes):
        jogo = sorted(random.sample(range(1, 26), 15))
        score = calcular_score(jogo, freq_total, freq_recente, atraso)
        jogos.append((jogo, score))

    jogos.sort(key=lambda x: x[1], reverse=True)

    return jogos[:quantidade]