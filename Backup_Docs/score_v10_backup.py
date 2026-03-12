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
    PESO_SOMA            = 0.20
    PESO_FAIXAS          = 0.10
    PESO_REPETICAO       = 0.10

    # Soma "ideal" observada no V9 (média ≈ 221,77)
    MEDIA_SOMA_V9        = 222.0
    DESVIO_SOMA_V9       = 20.0  # desvio relativamente largo para não ficar super rígido

    # Faixas da Lotofácil (1-5, 6-10, 11-15, 16-20, 21-25)
    # Médias observadas no V9: 1.92, 2.52, 3.02, 3.55, 3.98
    # Transformamos isso em "target" de distribuição relativa
    TARGET_FAIXAS_V9     = [1.9, 2.5, 3.0, 3.6, 4.0]

    # Janela de recência para frequência recente
    JANELA_RECENCIA      = 50

    # Repetição "ideal" observada no V9 (~7.14)
    # Vamos considerar ideal entre 7 e 8
    REPETICAO_ALVO_MIN   = 7
    REPETICAO_ALVO_MAX   = 8

    # Penalização por sequência longa
    PENALIDADE_SEQ_6     = 0.03
    PENALIDADE_SEQ_8     = 0.07
    PENALIDADE_SEQ_10    = 0.15


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
# DETECÇÃO DE CICLO (como antes, mas simplificada)
# ==========================================

def detectar_ciclo(concursos: List[Concurso]) -> ResultadoCiclo:
    if not concursos:
        return ResultadoCiclo("BALANCEADO", 0.0, ScoreConfigV10.PESO_RECENCIA_BASE)

    janela = concursos[-ScoreConfigV10.JANELA_RECENCIA:]
    total = concursos

    freq_total   = Counter(d for c in total  for d in c.dezenas)
    freq_recente = Counter(d for c in janela for d in c.dezenas)

    n_total   = sum(freq_total.values()) or 1
    n_recente = sum(freq_recente.values()) or 1

    divergencias = []
    for dezena in range(1, 26):
        p_total   = freq_total.get(dezena, 0) / n_total
        p_recente = freq_recente.get(dezena, 0) / n_recente
        divergencias.append(abs(p_recente - p_total))

    indice_volatilidade = sum(divergencias) / len(divergencias)

    # Ajuste bem simples de ciclo → peso de recência
    if indice_volatilidade < 0.003:
        return ResultadoCiclo("CONSERVADOR", indice_volatilidade, ScoreConfigV10.PESO_RECENCIA_BASE * 0.8)
    elif indice_volatilidade < 0.007:
        return ResultadoCiclo("BALANCEADO",  indice_volatilidade, ScoreConfigV10.PESO_RECENCIA_BASE * 1.0)
    else:
        return ResultadoCiclo("AGRESSIVO",   indice_volatilidade, ScoreConfigV10.PESO_RECENCIA_BASE * 1.2)


# ==========================================
# COMPONENTES DO SCORE
# ==========================================

def _score_frequencia(dezenas, freq_total: Counter, n_total: int) -> float:
    if n_total == 0:
        return 0.5
    valores = [freq_total.get(d, 0) / n_total for d in dezenas]
    # Escala em algo comparável (0–25)
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
    # Calcula, para cada dezena, há quantos concursos ela não sai
    for dezena in range(1, 26):
        atraso = 0
        for c in reversed(concursos):
            if dezena in c.dezenas:
                break
            atraso += 1
        atraso_map[dezena] = atraso

    max_atraso = max(atraso_map.values()) or 1
    # Quanto mais atraso, maior o score (normalizado 0–1)
    valores = [atraso_map.get(d, 0) / max_atraso for d in dezenas]
    return sum(valores) / len(valores)


def _score_soma(dezenas) -> float:
    soma = sum(dezenas)
    # Gaussiana centrada na média observada do V9 (~222)
    diff = soma - ScoreConfigV10.MEDIA_SOMA_V9
    sigma2 = 2 * (ScoreConfigV10.DESVIO_SOMA_V9 ** 2)
    gauss = math.exp(-(diff ** 2) / sigma2)
    # gauss já está entre ~0 e 1; podemos usar direto
    return gauss


def _score_faixas_v9_like(dezenas) -> float:
    # Conta quantas dezenas em cada faixa
    faixas = [0, 0, 0, 0, 0]
    for d in dezenas:
        if 1 <= d <= 5:
            faixas[0] += 1
        elif 6 <= d <= 10:
            faixas[1] += 1
        elif 11 <= d <= 15:
            faixas[2] += 1
        elif 16 <= d <= 20:
            faixas[3] += 1
        elif 21 <= d <= 25:
            faixas[4] += 1

    # Compara com o target médio do V9: [1.9, 2.5, 3.0, 3.6, 4.0]
    erro_total = 0.0
    for valor, alvo in zip(faixas, ScoreConfigV10.TARGET_FAIXAS_V9):
        erro_total += abs(valor - alvo)

    # Quanto menor o erro total, maior o score (normaliza em ~0–1)
    # Erro máximo razoável: se todas as 15 dezenas caíssem em uma faixa só seria bem alto.
    # Vamos tratar erro_total 0 -> score 1.0; erro_total >= 10 -> score ~0.0
    return 1.0 / (1.0 + erro_total)


def _score_repeticao_com_ultimo(jogo: Concurso, concursos: List[Concurso]) -> float:
    if not concursos:
        return 0.5

    ultimo = concursos[-1]  # último concurso disponível no momento
    conj_ultimo = set(ultimo.dezenas)
    repetidas = sum(1 for d in jogo.dezenas if d in conj_ultimo)

    # Queremos algo em torno de 7–8 como ideal
    if repetidas < ScoreConfigV10.REPETICAO_ALVO_MIN:
        # penaliza se for muito baixo
        diff = ScoreConfigV10.REPETICAO_ALVO_MIN - repetidas
    elif repetidas > ScoreConfigV10.REPETICAO_ALVO_MAX:
        diff = repetidas - ScoreConfigV10.REPETICAO_ALVO_MAX
    else:
        diff = 0

    # diff 0 -> score 1.0; diff >= 5 -> score ~0
    return 1.0 / (1.0 + diff)


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
    """
    Calcula o score V10 para um jogo, usando:
    - frequência histórica
    - frequência recente (com peso dinâmico pelo ciclo)
    - atraso
    - soma (calibrada para o perfil do V9)
    - distribuição por faixas (imitando o V9)
    - repetição com o último concurso (ideal ~7–8)
    - penalização de sequência longa
    """
    # Freq. histórica e recente
    freq_total = Counter(d for c in concursos for d in c.dezenas)
    janela = concursos[-ScoreConfigV10.JANELA_RECENCIA:] if concursos else []
    freq_recente = Counter(d for c in janela for d in c.dezenas)

    n_total = sum(freq_total.values()) or 1
    n_recente = sum(freq_recente.values()) or 1

    # Ciclo atual
    ciclo = detectar_ciclo(concursos)

    # Componentes
    sf = _score_frequencia(jogo.dezenas, freq_total, n_total)
    sr = _score_recencia(jogo.dezenas, freq_recente, n_recente)
    sa = _score_atraso(jogo.dezenas, concursos)
    ss = _score_soma(jogo.dezenas)
    sfx = _score_faixas_v9_like(jogo.dezenas)
    srep = _score_repeticao_com_ultimo(jogo, concursos)
    pen_seq = _penalidade_sequencia(jogo.dezenas)

    # Combinação com pesos (recência ajustada pelo ciclo)
    score_final = (
        ScoreConfigV10.PESO_FREQUENCIA    * sf +
        ciclo.peso_recencia              * sr +
        ScoreConfigV10.PESO_ATRASO       * sa +
        ScoreConfigV10.PESO_SOMA         * ss +
        ScoreConfigV10.PESO_FAIXAS       * sfx +
        ScoreConfigV10.PESO_REPETICAO    * srep
    ) - pen_seq

    return ResultadoScore(
        score_final=round(score_final, 6),
        score_frequencia=round(sf, 6),
        score_recencia=round(sr, 6),
        score_atraso=round(sa, 6),
        score_soma=round(ss, 6),
        score_faixas=round(sfx, 6),
        score_repeticao=round(srep, 6),
        penalidade_sequencia=round(pen_seq, 6),
        ciclo=ciclo.ciclo,
        indice_volatilidade=round(ciclo.indice_volatilidade, 6),
    )