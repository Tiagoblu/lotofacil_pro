import random


def gerar_frequencia_simulada():
    """
    Simula frequência histórica coerente.
    Distribuição quase normal entre 10 e 40.
    """
    return {i: random.randint(15, 35) for i in range(1, 26)}


def calcular_metricas(jogo):
    """
    Retorna métricas estruturais do jogo.
    """

    pares = sum(1 for n in jogo if n % 2 == 0)
    impares = 15 - pares
    soma = sum(jogo)

    blocos = [
        sum(1 for n in jogo if 1 <= n <= 5),
        sum(1 for n in jogo if 6 <= n <= 10),
        sum(1 for n in jogo if 11 <= n <= 15),
        sum(1 for n in jogo if 16 <= n <= 20),
        sum(1 for n in jogo if 21 <= n <= 25),
    ]

    return {
        "pares": pares,
        "impares": impares,
        "soma": soma,
        "blocos": blocos,
    }