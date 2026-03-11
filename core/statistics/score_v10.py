# core/statistics/score_v10.py

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List

from core.domain.models import Concurso


# ==========================================
# CONFIGURAÇÃO CENTRAL DO V10
# ==========================================

class ScoreConfigV10:
    # Pesos dos componentes
    PESO_FREQUENCIA  = 0.30
    PESO_RECENCIA    = 0.25
    PESO_ATRASO      = 0.20
    PESO_SOMA        = 0.15
    PESO_DISTRIBUICAO = 0.10

    # Soma ideal histórica da Lotofácil
    MEDIA_SOMA  = 193.0
    DESVIO_SOMA = 25.0

    # Penalização de sequência
    PENALIDADE_SEQ_6  = 0.05
    PENALIDADE_SEQ_8  = 0.10
    PENALIDADE_SEQ_10 = 0.20

    # Janela de recência
    JANELA_RECENCIA = 50


# ==========================================
# RESULTADO DO CICLO
# ==========================================

@dataclass
class ResultadoCiclo:
    ciclo: str
    indice_volatilidade: float
    peso_recencia: float


# ==========================================
# RESULTADO DO SCORE
# ==========================================

@dataclass
class ResultadoScore:
    score_final: float
    score_frequencia: float
    score_recencia: float
    score_atraso: float
    score_soma: float
    score_distribuicao: float
    penalidade: float


# ==========================================
# DETECÇÃO DE CICLO
# ==========================================

def detectar_ciclo(concursos: List[Concurso]) -> ResultadoCiclo:
    janela = concursos[-ScoreConfigV10.JANELA_RECENCIA:]
    total = concursos

    freq_total   = Counter(d for c in total  for d in c.dezenas)
    freq_recente = Counter(d for c in janela for d in c.dezenas)

    n_total   = sum(freq_total.values())
    n_recente = sum(freq_recente.values())

    divergencias = []
    for dezena in range(1, 26):
        p_total   = freq_total.get(dezena, 0)   / n_total   if n_total   > 0 else 0
        p_recente = freq_recente.get(dezena, 0) / n_recente if n_recente > 0 else 0
        divergencias.append(abs(p_recente - p_total))

    indice_volatilidade = sum(divergencias) / len(divergencias)

    if indice_volatilidade < 0.003:
        return ResultadoCiclo("CONSERVADOR", indice_volatilidade, 0.50)
    elif indice_volatilidade < 0.007:
        return ResultadoCiclo("BALANCEADO",  indice_volatilidade, 0.65)
    else:
        return ResultadoCiclo("AGRESSIVO",   indice_volatilidade, 0.80)


# ==========================================
# COMPONENTES DO SCORE
# ==========================================

def _score_frequencia(dezenas, freq_total, n_total) -> float:
    if n_total == 0:
        return 0.5
    scores = [freq_total.get(d, 0) / n_total for d in dezenas]
    return sum(scores) / len(scores) * 25


def _score_recencia(dezenas, freq_recente, n_recente) -> float:
    if n_recente == 0:
        return 0.5
    scores = [freq_recente.get(d, 0) / n_recente for d in dezenas]
    return sum(scores) / len(scores) * 25


def _score_atraso(dezenas, concursos) -> float:
    ultimo_numero = concursos[-1].numero if concursos[-1].numero > 0 else len(concursos)
    atraso_map = {}
    for dezena in range(1, 26):
        for i, c in enumerate(reversed(concursos)):
            if dezena in c.dezenas:
                atraso_map[dezena] = i
                break
        else:
            atraso_map[dezena] = len(concursos)

    max_atraso = max(atraso_map.values()) if atraso_map else 1
    if max_atraso == 0:
        return 0.5

    scores = [atraso_map.get(d, 0) / max_atraso for d in dezenas]
    return sum(scores) / len(scores)


def _score_soma(dezenas) -> float:
    soma = sum(dezenas)
    diferenca = soma - ScoreConfigV10.MEDIA_SOMA
    return math.exp(
        -(diferenca ** 2) /
        (2 * ScoreConfigV10.DESVIO_SOMA ** 2)
    )


def _score_distribuicao(dezenas) -> float:
    linhas = [0, 0, 0, 0, 0]
    for d in dezenas:
        if d <= 5:
            linhas[0] += 1
        elif d <= 10:
            linhas[1] += 1
        elif d <= 15:
            linhas[2] += 1
        elif d <= 20:
            linhas[3] += 1
        else:
            linhas[4] += 1
    ideal = 3
    erro = sum(abs(l - ideal) for l in linhas)
    return 1 / (1 + erro)


def _penalidade_sequencia(dezenas) -> float:
    ordenadas = sorted(dezenas)
    maior_seq = 1
    atual = 1
    for i in range(1, len(ordenadas)):
        if ordenadas[i] == ordenadas[i - 1] + 1:
            atual += 1
            maior_seq = max(maior_seq, atual)
        else:
            atual = 1
    if maior_seq >= 10:
        return ScoreConfigV10.PENALIDADE_SEQ_10
    elif maior_seq >= 8:
        return ScoreConfigV10.PENALIDADE_SEQ_8
    elif maior_seq >= 6:
        return ScoreConfigV10.PENALIDADE_SEQ_6
    return 0.0


# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================

def calcular(jogo: Concurso, concursos: List[Concurso]) -> ResultadoScore:
    janela = concursos[-ScoreConfigV10.JANELA_RECENCIA:]

    freq_total   = Counter(d for c in concursos for d in c.dezenas)
    freq_recente = Counter(d for c in janela    for d in c.dezenas)

    n_total   = sum(freq_total.values())
    n_recente = sum(freq_recente.values())

    ciclo = detectar_ciclo(concursos)

    sf  = _score_frequencia(jogo.dezenas, freq_total,   n_total)
    sr  = _score_recencia(  jogo.dezenas, freq_recente, n_recente)
    sa  = _score_atraso(    jogo.dezenas, concursos)
    ss  = _score_soma(      jogo.dezenas)
    sd  = _score_distribuicao(jogo.dezenas)
    pen = _penalidade_sequencia(jogo.dezenas)

    # Peso de recência varia com o ciclo detectado
    peso_recencia_dinamico = ciclo.peso_recencia

    score_final = (
        ScoreConfigV10.PESO_FREQUENCIA   * sf  +
        peso_recencia_dinamico           * sr  +
        ScoreConfigV10.PESO_ATRASO       * sa  +
        ScoreConfigV10.PESO_SOMA         * ss  +
        ScoreConfigV10.PESO_DISTRIBUICAO * sd
    ) - pen

    return ResultadoScore(
        score_final=round(score_final, 6),
        score_frequencia=round(sf,  6),
        score_recencia=round(sr,    6),
        score_atraso=round(sa,      6),
        score_soma=round(ss,        6),
        score_distribuicao=round(sd, 6),
        penalidade=round(pen,       6),
    )