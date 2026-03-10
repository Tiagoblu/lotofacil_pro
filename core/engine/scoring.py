# core/engine/scoring.py
"""
Módulo de scoring agressivo legado.

Este módulo implementa um cálculo de score simples, baseado em:
    - frequência total
    - frequência recente
    - atraso
    - ajustes estruturais (pares, soma)
    - penalização progressiva por sequências longas

Ele é mantido como alternativa/experimento em paralelo ao score V9
(core.statistics.score_calculator) e ao score V10
(core.statistics.score_v10).
"""


def calcular_penalizacao_sequencia(jogo: list[int]) -> float:
    """
    Calcula um fator multiplicativo de penalização com base na maior
    sequência consecutiva presente no jogo.

    Retorna um número em [0, 1]:
        - 1.00: nenhuma sequência problemática
        - 0.92: sequências moderadas (>= 6)
        - 0.85: sequências longas (>= 8)
        - 0.75: sequências muito longas (>= 10)
    """
    jogo_ordenado = sorted(jogo)
    maior_seq = 1
    seq_atual = 1

    for i in range(1, len(jogo_ordenado)):
        if jogo_ordenado[i] == jogo_ordenado[i - 1] + 1:
            seq_atual += 1
            maior_seq = max(maior_seq, seq_atual)
        else:
            seq_atual = 1

    if maior_seq >= 10:
        return 0.75
    elif maior_seq >= 8:
        return 0.85
    elif maior_seq >= 6:
        return 0.92
    else:
        return 1.0


def calcular_score(
    jogo: list[int],
    freq_total: dict[int, int],
    freq_recente: dict[int, int],
    atraso: dict[int, int],
) -> float:
    """
    Calcula um score agressivo para um jogo, usando frequências
    históricas, frequências recentes, atraso e critérios estruturais
    simples (par/ímpar, faixa de soma e sequências).

    Args:
        jogo: lista de dezenas inteiras (ex.: [1,2,...,25]).
        freq_total: mapa de dezena -> frequência no histórico completo.
        freq_recente: mapa de dezena -> frequência em janela recente.
        atraso: mapa de dezena -> atraso em concursos.

    Returns:
        Score como float (valores maiores indicam jogos mais "atrativos"
        segundo este critério agressivo).
    """
    score = 0.0

    # Frequência histórica (peso base)
    for dezena in jogo:
        score += freq_total.get(dezena, 0) * 1.0

    # Frequência recente (peso maior)
    for dezena in jogo:
        score += freq_recente.get(dezena, 0) * 1.5

    # Atraso (perfil agressivo)
    for dezena in jogo:
        score += atraso.get(dezena, 0) * 0.8

    pares = sum(1 for n in jogo if n % 2 == 0)
    soma = sum(jogo)

    # Par/ímpar ideal
    if 6 <= pares <= 9:
        score += 15.0

    # Faixa de soma ideal
    if 170 <= soma <= 230:
        score += 20.0

    # Penalização estrutural por sequência longa (fator multiplicativo)
    penalizacao = calcular_penalizacao_sequencia(jogo)
    score = score * penalizacao

    return float(score)