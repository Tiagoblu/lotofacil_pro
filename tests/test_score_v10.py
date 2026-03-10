# tests/test_score_v10.py

import math
import builtins

import pytest

from core.statistics.score_v10 import (
    calcular,
    detectar_ciclo,
    ResultadoScore,
    ResultadoCiclo,
)


class ConcursoFake:
    """
    Modelo mínimo para simular um concurso em testes,
    compatível com o que score_v10 espera: atributo `dezenas`.
    """
    def __init__(self, dezenas):
        self.dezenas = dezenas


class JogoFake:
    """
    Modelo mínimo para simular um jogo em testes,
    compatível com o que score_v10 espera: atributo `dezenas`.
    """
    def __init__(self, dezenas):
        self.dezenas = dezenas


def _gerar_historico_basico():
    """
    Gera um pequeno histórico artificial de concursos para testes.

    Propriedades:
    - 10 concursos
    - Dezenas variando de forma moderadamente estável
    """
    historico = []

    # Começa com um padrão bem regular
    historico.append(ConcursoFake([1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                   11, 12, 13, 14, 15]))
    historico.append(ConcursoFake([2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                   12, 13, 14, 15, 16]))
    historico.append(ConcursoFake([3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                   13, 14, 15, 16, 17]))
    historico.append(ConcursoFake([4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                                   14, 15, 16, 17, 18]))
    historico.append(ConcursoFake([5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                                   15, 16, 17, 18, 19]))
    historico.append(ConcursoFake([6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                                   16, 17, 18, 19, 20]))
    historico.append(ConcursoFake([7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                                   17, 18, 19, 20, 21]))
    historico.append(ConcursoFake([8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                                   18, 19, 20, 21, 22]))
    historico.append(ConcursoFake([9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                   19, 20, 21, 22, 23]))
    historico.append(ConcursoFake([10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                   20, 21, 22, 23, 24]))

    return historico


# ──────────────────────────────────────────────
# Testes para detectar_ciclo
# ──────────────────────────────────────────────

def test_detectar_ciclo_retorna_estrutura_valida():
    historico = _gerar_historico_basico()

    resultado = detectar_ciclo(historico)

    assert isinstance(resultado, ResultadoCiclo)
    assert resultado.ciclo in {"CONSERVADOR", "BALANCEADO", "AGRESSIVO"}
    assert 0.0 <= resultado.indice_volatilidade <= 1.0
    assert 0.0 <= resultado.peso_recencia <= 1.0


def test_detectar_ciclo_historia_pequena():
    # Histórico com apenas 1 concurso deve cair no caminho "seguro"
    historico = [ConcursoFake([1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                               11, 12, 13, 14, 15])]

    resultado = detectar_ciclo(historico)

    assert isinstance(resultado, ResultadoCiclo)
    # Por padrão, definimos BALANCEADO quando histórico é muito pequeno
    assert resultado.ciclo == "BALANCEADO"


# ──────────────────────────────────────────────
# Testes para calcular (score V10)
# ──────────────────────────────────────────────

def test_calcular_score_v10_retorna_resultado_valido():
    historico = _gerar_historico_basico()
    # Jogo razoavelmente alinhado com o padrão do histórico
    jogo = JogoFake([5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                     15, 16, 17, 18, 19])

    resultado = calcular(jogo, historico)

    assert isinstance(resultado, ResultadoScore)
    # Score não precisa estar entre 0 e 1 por causa do bônus,
    # mas deve ser um número finito
    assert isinstance(resultado.score_final, float)
    assert math.isfinite(resultado.score_final)

    assert resultado.ciclo in {"CONSERVADOR", "BALANCEADO", "AGRESSIVO"}
    assert 0.0 <= resultado.indice_volatilidade <= 1.0
    assert 0.0 <= resultado.peso_recencia <= 1.0
    # Repetições não podem ser negativas nem maiores que 15
    assert 0 <= resultado.repeticoes <= 15


def test_calcular_dispara_erro_quando_jogo_invalido():
    historico = _gerar_historico_basico()
    # Jogo com quantidade errada de dezenas
    jogo_invalido = JogoFake([1, 2, 3])  # só 3 dezenas

    with pytest.raises(ValueError):
        calcular(jogo_invalido, historico)


def test_calcular_dispara_erro_quando_historico_vazio():
    historico_vazio = []
    jogo = JogoFake([1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                     11, 12, 13, 14, 15])

    with pytest.raises(ValueError):
        calcular(jogo, historico_vazio)