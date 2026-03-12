# core/statistics/score_v10.py

import math
from collections import Counter
from dataclasses import dataclass
from typing import List

from core.domain.models import Concurso


# ==========================================
# CONFIGURAÇÃO CENTRAL DO V10
# ==========================================

class ScoreConfigV10:
    # Pesos dos componentes principais
    PESO_FREQUENCIA      = 0.20
    PESO_RECENCIA_BASE   = 0.25
    PESO_ATRASO          = 0.15
    PESO_SOMA            = 0.35
    PESO_FAIXAS          = 0.20
    PESO_REPETICAO       = 0.30

    # Soma ideal do V9
    MEDIA_SOMA_V9        = 222.0
    DESVIO_SOMA_V9       = 14.0

    # Faixas alvo DNA V9
    TARGET_FAIXAS_V9     = [1.9, 2.5, 2.4, 3.6, 4.0]

    # Janela de recência
    JANELA_RECENCIA      = 50

    # Repetição ideal 7-8
    REPETICAO_ALVO_MIN   = 7
    REPETICAO_ALVO_MAX   = 8

    # Penalização sequência longa
    PENALIDADE_SEQ_6     = 0.03
    PENALIDADE_SEQ_8     = 0.07
    PENALIDADE_SEQ_10    = 0.15

    # Penalização faixa 11-15 quando >= 4 dezenas no miolo
    PENALIDADE_FAIXA_MID_LIMIAR  = 4
    PENALIDADE_FAIXA_MID_POR_DEZ = 0.04

    # Equilíbrio par/ímpar — alvo V9: 7.21 pares / 7.79 ímpares
    # Penaliza quando pares > 8 ou pares < 6
    PARES_ALVO_MIN       = 6
    PARES_ALVO_MAX       = 8
    PENALIDADE_PAR_POR_U = 0.04   # por unidade fora do intervalo


# ==========================================
# TIPOS DE RESULTADO
# ==========================================

@dataclass
class ResultadoCiclo:
    ciclo: str
    indice_volatilidade: float
    peso_recencia: float


@dataclass
class ResultadoScore:
    score_final: float
    score_frequencia: float
    score_recencia: float
    score_atraso: float
    score_soma: float
    score_faixas: float
    score_repeticao: float
    penalidade_sequencia: float
    ciclo: str
    indice_volatilidade: float


# ==========================================
# DETECÇÃO DE CICLO
# ==========================================

def detectar_ciclo(concursos: List[Concurso]) -> ResultadoCiclo:
    if not concursos:
        return ResultadoCiclo("BALANCEADO", 0.0, ScoreConfigV10.PESO_RECENCIA_BASE)

    janela = concursos[-ScoreConfigV10.JANELA_RECENCIA:]
    total  = concursos

    freq_total   = Counter(d for c in total  for d in c.dezenas)
    freq_recente = Counter(d for c in janela for d in c.dezenas)

    n_total   = sum(freq_total.values())   or 1
    n_recente = sum(freq_recente.values()) or 1

    divergencias = []
    for dezena in range(1, 26):
        p_total   = freq_total.get(dezena, 0)   / n_total
        p_recente = freq_recente.get(dezena, 0) / n_recente
        divergencias.append(abs(p_recente - p_total))

    indice_volatilidade = sum(divergencias) / len(divergencias)

    if indice_volatilidade < 0.003:
        return ResultadoCiclo(
            "CONSERVADOR", indice_volatilidade,
            ScoreConfigV10.PESO_RECENCIA_BASE * 0.8
        )
    elif indice_volatilidade < 0.007:
        return ResultadoCiclo(
            "BALANCEADO", indice_volatilidade,
            ScoreConfigV10.PESO_RECENCIA_BASE * 1.0
        )
    else:
        return ResultadoCiclo(
            "AGRESSIVO", indice_volatilidade,
            ScoreConfigV10.PESO_RECENCIA_BASE * 1.2
        )


# ==========================================
# COMPONENTES DO SCORE
# ==========================================

def _score_frequencia(dezenas, freq_total: Counter, n_total: int) -> float:
    if n_total == 0:
        return 0.5
    valores = [freq_total.get(d, 0) / n_total for d in dezenas]
    return (sum(valores) / len(valores)) * 25.0


def _score_recencia(dezenas, freq_recente: Counter, n_recente: int) -> float:
    if n_recente == 0:
        return 0.5
    valores = [freq_recente.get(d, 0) / n_recente for d in dezenas]
    return (sum(valores) / len(valores)) * 25.0


def _score_atraso(dezenas, concursos: List[Concurso]) -> float:
    if not concursos:
        return 0.5

    atraso_map = {}
    for dezena in range(1, 26):
        atraso = 0
        for c in reversed(concursos):
            if dezena in c.dezenas:
                break
            atraso += 1
        atraso_map[dezena] = atraso

    max_atraso = max(atraso_map.values()) or 1
    valores = [atraso_map.get(d, 0) / max_atraso for d in dezenas]
    return sum(valores) / len(valores)


def _score_soma(dezenas) -> float:
    soma   = sum(dezenas)
    diff   = soma - ScoreConfigV10.MEDIA_SOMA_V9
    sigma2 = 2 * (ScoreConfigV10.DESVIO_SOMA_V9 ** 2)
    return math.exp(-(diff ** 2) / sigma2)


def _score_faixas_v9_like(dezenas) -> float:
    faixas = [0, 0, 0, 0, 0]
    for d in dezenas:
        if   1  <= d <= 5:  faixas[0] += 1
        elif 6  <= d <= 10: faixas[1] += 1
        elif 11 <= d <= 15: faixas[2] += 1
        elif 16 <= d <= 20: faixas[3] += 1
        elif 21 <= d <= 25: faixas[4] += 1

    erro_total = sum(
        abs(valor - alvo)
        for valor, alvo in zip(faixas, ScoreConfigV10.TARGET_FAIXAS_V9)
    )
    return 1.0 / (1.0 + erro_total)


def _penalidade_faixa_mid(dezenas) -> float:
    """
    Penalidade extra para jogos com 4+ dezenas na faixa 11-15.
    """
    count_mid = sum(1 for d in dezenas if 11 <= d <= 15)
    if count_mid >= ScoreConfigV10.PENALIDADE_FAIXA_MID_LIMIAR:
        excesso = count_mid - ScoreConfigV10.PENALIDADE_FAIXA_MID_LIMIAR + 1
        return excesso * ScoreConfigV10.PENALIDADE_FAIXA_MID_POR_DEZ
    return 0.0


def _penalidade_paridade(dezenas) -> float:
    """
    Penaliza jogos com pares fora do intervalo 6-8.
    Alvo V9: 7.21 pares em média.
    """
    pares = sum(1 for d in dezenas if d % 2 == 0)
    if pares < ScoreConfigV10.PARES_ALVO_MIN:
        excesso = ScoreConfigV10.PARES_ALVO_MIN - pares
    elif pares > ScoreConfigV10.PARES_ALVO_MAX:
        excesso = pares - ScoreConfigV10.PARES_ALVO_MAX
    else:
        excesso = 0
    return excesso * ScoreConfigV10.PENALIDADE_PAR_POR_U


def _score_repeticao_com_ultimo(jogo: Concurso, concursos: List[Concurso]) -> float:
    if not concursos:
        return 0.5

    ultimo      = concursos[-1]
    conj_ultimo = set(ultimo.dezenas)
    repetidas   = sum(1 for d in jogo.dezenas if d in conj_ultimo)

    if repetidas < ScoreConfigV10.REPETICAO_ALVO_MIN:
        diff = ScoreConfigV10.REPETICAO_ALVO_MIN - repetidas
    elif repetidas > ScoreConfigV10.REPETICAO_ALVO_MAX:
        diff = repetidas - ScoreConfigV10.REPETICAO_ALVO_MAX
    else:
        diff = 0

    return 1.0 / (1.0 + diff * 0.5)


def _penalidade_sequencia(dezenas) -> float:
    ordenadas = sorted(dezenas)
    maior_seq = 1
    atual     = 1
    for i in range(1, len(ordenadas)):
        if ordenadas[i] == ordenadas[i-1] + 1:
            atual    += 1
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
    """
    Calcula o score V10 para um jogo.

    Componentes:
        - Frequência histórica
        - Frequência recente  (peso dinâmico via detectar_ciclo)
        - Atraso
        - Soma               (gaussiana centrada em 222, desvio 14)
        - Faixas             (distância ao DNA do V9)
        - Repetição          (penalização severa fora de 7-8)
        - Penalidade sequência longa  (>= 6 consecutivas)
        - Penalidade faixa 11-15      (>= 4 dezenas no miolo)
        - Penalidade paridade         (pares fora de 6-8)
    """
    freq_total   = Counter(d for c in concursos for d in c.dezenas)
    janela       = concursos[-ScoreConfigV10.JANELA_RECENCIA:] if concursos else []
    freq_recente = Counter(d for c in janela for d in c.dezenas)

    n_total   = sum(freq_total.values())   or 1
    n_recente = sum(freq_recente.values()) or 1

    ciclo = detectar_ciclo(concursos)

    sf      = _score_frequencia(jogo.dezenas, freq_total,   n_total)
    sr      = _score_recencia  (jogo.dezenas, freq_recente, n_recente)
    sa      = _score_atraso    (jogo.dezenas, concursos)
    ss      = _score_soma      (jogo.dezenas)
    sfx     = _score_faixas_v9_like(jogo.dezenas)
    srep    = _score_repeticao_com_ultimo(jogo, concursos)
    pen_seq = _penalidade_sequencia(jogo.dezenas)
    pen_mid = _penalidade_faixa_mid(jogo.dezenas)
    pen_par = _penalidade_paridade(jogo.dezenas)

    score_final = (
        ScoreConfigV10.PESO_FREQUENCIA * sf  +
        ciclo.peso_recencia            * sr  +
        ScoreConfigV10.PESO_ATRASO     * sa  +
        ScoreConfigV10.PESO_SOMA       * ss  +
        ScoreConfigV10.PESO_FAIXAS     * sfx +
        ScoreConfigV10.PESO_REPETICAO  * srep
    ) - pen_seq - pen_mid - pen_par

    return ResultadoScore(
        score_final          = round(score_final, 6),
        score_frequencia     = round(sf,      6),
        score_recencia       = round(sr,      6),
        score_atraso         = round(sa,      6),
        score_soma           = round(ss,      6),
        score_faixas         = round(sfx,     6),
        score_repeticao      = round(srep,    6),
        penalidade_sequencia = round(pen_seq + pen_mid + pen_par, 6),
        ciclo                = ciclo.ciclo,
        indice_volatilidade  = round(ciclo.indice_volatilidade, 6),
    )