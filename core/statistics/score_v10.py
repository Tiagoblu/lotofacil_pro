# core/statistics/score_v10.py
"""
Score V10 – Score Estrutural Adaptativo com Detecção de Ciclo

Fórmula:
    S_total = 0.60 * S_freq_hibrida + 0.25 * S_atraso + bonus_repeticao

Onde:
    S_freq_hibrida = peso_recencia * freq_recente + peso_historico * freq_historica
    peso_recencia e peso_historico são definidos dinamicamente via detectar_ciclo()

Todos os sub-scores são normalizados individualmente por dezena (0-1)
antes da agregação, garantindo que S_total seja comparável entre jogos.
"""

from __future__ import annotations

import logging
from statistics import mean, pstdev
from typing import Dict, List, NamedTuple, Tuple

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Configuração dos pesos (fonte única de verdade)
# ──────────────────────────────────────────────

JANELA_CICLO: int = 50          # concursos usados para detectar ciclo
JANELA_RECENCIA: int = 20       # concursos usados para freq recente

PESO_FREQ_NO_SCORE: float = 0.60
PESO_ATRASO_NO_SCORE: float = 0.25
# (soma = 0.85; os 0.15 restantes vêm do bônus de repetição no máximo)

LIMIAR_AGRESSIVO: float = 0.6
LIMIAR_CONSERVADOR: float = 0.4

PESOS_CICLO: Dict[str, float] = {
    "AGRESSIVO":   0.75,   # peso da recência
    "BALANCEADO":  0.65,
    "CONSERVADOR": 0.50,
}

BONUS_REPETICAO: Dict[Tuple[int, int], float] = {
    (8, 10): 0.15,
    (6, 7):  0.05,
}
PENALIZACAO_REPETICAO_EXCESSIVA: float = -0.10
LIMIAR_REPETICAO_EXCESSIVA: int = 12


# ──────────────────────────────────────────────
# Tipos auxiliares
# ──────────────────────────────────────────────

class ResultadoCiclo(NamedTuple):
    ciclo: str
    indice_volatilidade: float
    peso_recencia: float


class ResultadoScore(NamedTuple):
    score_final: float
    ciclo: str
    indice_volatilidade: float
    peso_recencia: float
    repeticoes: int


# ──────────────────────────────────────────────
# Funções internas (privadas)
# ──────────────────────────────────────────────

def _normalizar(valor: float, max_valor: float) -> float:
    """Normaliza um valor para o intervalo [0, 1]."""
    if max_valor == 0:
        return 0.0
    return min(valor / max_valor, 1.0)


def _calcular_freq_historica(concursos: list) -> Dict[int, int]:
    """Calcula frequência absoluta de cada dezena no histórico completo."""
    freq: Dict[int, int] = {n: 0 for n in range(1, 26)}
    for c in concursos:
        for d in c.dezenas:
            freq[d] += 1
    return freq


def _calcular_freq_recente(concursos: list, janela: int) -> Dict[int, int]:
    """Calcula frequência absoluta de cada dezena nos últimos N concursos."""
    freq: Dict[int, int] = {n: 0 for n in range(1, 26)}
    for c in concursos[-janela:]:
        for d in c.dezenas:
            freq[d] += 1
    return freq


def _calcular_atraso(concursos: list) -> Dict[int, int]:
    """
    Calcula o atraso de cada dezena (quantos concursos desde a última saída).
    Dezenas que nunca saíram recebem o atraso máximo = len(concursos).
    """
    atraso: Dict[int, int] = {n: len(concursos) for n in range(1, 26)}
    for i, c in enumerate(reversed(concursos)):
        for d in c.dezenas:
            if atraso[d] == len(concursos):  # ainda não encontrou
                atraso[d] = i
    return atraso


def _bonus_por_repeticao(repeticoes: int) -> float:
    """Retorna o bônus ou penalização baseado no número de repetições."""
    if repeticoes >= LIMIAR_REPETICAO_EXCESSIVA:
        return PENALIZACAO_REPETICAO_EXCESSIVA
    for (minimo, maximo), bonus in BONUS_REPETICAO.items():
        if minimo <= repeticoes <= maximo:
            return bonus
    return 0.0


# ──────────────────────────────────────────────
# API pública
# ──────────────────────────────────────────────

def detectar_ciclo(concursos: list) -> ResultadoCiclo:
    """
    Detecta o ciclo estatístico atual com base nos últimos N concursos.

    Calcula um índice de volatilidade composto por:
        - Variância da soma das dezenas (captura dispersão total)
        - Variância do número de pares (captura padrão par/ímpar)
        - Rotatividade: proporção de dezenas únicas que apareceram

    Retorna:
        ResultadoCiclo com o nome do ciclo, índice de volatilidade e
        peso da recência a ser usado no score híbrido.
    """
    if len(concursos) < 2:
        logger.warning(
            "Histórico insuficiente para detectar ciclo (%d concursos). "
            "Usando BALANCEADO como padrão.",
            len(concursos)
        )
        return ResultadoCiclo("BALANCEADO", 0.5, PESOS_CICLO["BALANCEADO"])

    ultimos = concursos[-JANELA_CICLO:]

    somas = [sum(c.dezenas) for c in ultimos]
    pares = [sum(1 for n in c.dezenas if n % 2 == 0) for c in ultimos]

    var_soma = pstdev(somas) if len(somas) > 1 else 0.0
    var_pares = pstdev(pares) if len(pares) > 1 else 0.0

    dezenas_rotativas: set = set()
    for c in ultimos:
        dezenas_rotativas.update(c.dezenas)
    rotatividade = len(dezenas_rotativas) / 25

    var_soma_norm = min(var_soma / 40, 1.0)
    var_pares_norm = min(var_pares / 5, 1.0)

    indice_volatilidade = round(
        0.4 * var_soma_norm +
        0.3 * var_pares_norm +
        0.3 * rotatividade,
        6
    )

    if indice_volatilidade >= LIMIAR_AGRESSIVO:
        ciclo = "AGRESSIVO"
    elif indice_volatilidade <= LIMIAR_CONSERVADOR:
        ciclo = "CONSERVADOR"
    else:
        ciclo = "BALANCEADO"

    peso_recencia = PESOS_CICLO[ciclo]

    logger.debug(
        "Ciclo detectado: %s | volatilidade=%.4f | peso_recencia=%.2f",
        ciclo, indice_volatilidade, peso_recencia
    )

    return ResultadoCiclo(ciclo, indice_volatilidade, peso_recencia)


def calcular(jogo, concursos: list) -> ResultadoScore:
    """
    Calcula o score V10 de um jogo em relação ao histórico.

    O score é composto por:
        - Score de frequência híbrida (recente + histórica ponderadas pelo ciclo)
        - Score de atraso (favorece dezenas moderadamente atrasadas)
        - Bônus/penalização por repetição dos últimos 3 concursos

    Args:
        jogo: Objeto com atributo 'dezenas' (List[int] com 15 elementos).
        concursos: Lista de concursos históricos (do mais antigo ao mais recente).

    Returns:
        ResultadoScore com score_final e detalhes do ciclo.

    Raises:
        ValueError: Se jogo.dezenas não tiver 15 elementos ou concursos estiver vazio.
    """
    # Validação de entrada
    if not concursos:
        raise ValueError("Histórico de concursos não pode ser vazio.")
    if len(jogo.dezenas) != 15:
        raise ValueError(
            f"Jogo deve ter exatamente 15 dezenas. "
            f"Recebido: {len(jogo.dezenas)}."
        )

    # Detectar ciclo (único ponto de cálculo)
    resultado_ciclo = detectar_ciclo(concursos)
    peso_recencia = resultado_ciclo.peso_recencia
    peso_historico = 1.0 - peso_recencia

    # Calcular frequências (uma vez só)
    freq_historica = _calcular_freq_historica(concursos)
    freq_recente = _calcular_freq_recente(concursos, JANELA_RECENCIA)
    mapa_atraso = _calcular_atraso(concursos)

    max_hist = max(freq_historica.values()) if freq_historica else 1
    max_recente = max(freq_recente.values()) if freq_recente else 1
    max_atraso = max(mapa_atraso.values()) if mapa_atraso else 1

    # Calcular sub-scores por dezena
    scores_freq: List[float] = []
    scores_atraso: List[float] = []

    for dezena in jogo.dezenas:
        freq_hist_norm = _normalizar(freq_historica.get(dezena, 0), max_hist)
        freq_rec_norm = _normalizar(freq_recente.get(dezena, 0), max_recente)

        freq_hibrida = (
            peso_recencia * freq_rec_norm +
            peso_historico * freq_hist_norm
        )

        scores_freq.append(freq_hibrida)
        scores_atraso.append(_normalizar(mapa_atraso.get(dezena, 0), max_atraso))

    # Score médio por dezena (garante que cada componente fique em [0, 1])
    score_freq_medio = mean(scores_freq)
    score_atraso_medio = mean(scores_atraso)

    # Bônus de repetição (últimos 3 concursos)
    dezenas_ultimos_3: set = set()
    for c in concursos[-3:]:
        dezenas_ultimos_3.update(c.dezenas)
    repeticoes = len(set(jogo.dezenas) & dezenas_ultimos_3)
    bonus = _bonus_por_repeticao(repeticoes)

    # Score final
    score_final = round(
        PESO_FREQ_NO_SCORE * score_freq_medio +
        PESO_ATRASO_NO_SCORE * score_atraso_medio +
        bonus,
        6
    )

    logger.debug(
        "Score V10 | score=%.6f | ciclo=%s | freq=%.4f | atraso=%.4f | "
        "bonus=%.2f | repeticoes=%d",
        score_final,
        resultado_ciclo.ciclo,
        score_freq_medio,
        score_atraso_medio,
        bonus,
        repeticoes,
    )

    return ResultadoScore(
        score_final=score_final,
        ciclo=resultado_ciclo.ciclo,
        indice_volatilidade=resultado_ciclo.indice_volatilidade,
        peso_recencia=peso_recencia,
        repeticoes=repeticoes,
    )