from collections import Counter
from core.database import obter_todos_concursos


def carregar_historico():
    dados = obter_todos_concursos()
    historico = []

    for linha in dados:
        if not linha or not linha[0]:
            continue

        dezenas_brutas = linha[0]

        # aceita vírgula ou espaço automaticamente
        dezenas_str = dezenas_brutas.replace(",", " ").split()

        try:
            dezenas = [int(d) for d in dezenas_str]
            historico.append(dezenas)
        except ValueError:
            continue

    return historico


def frequencia_total(historico):
    contador = Counter()
    for jogo in historico:
        contador.update(jogo)
    return contador


def frequencia_recente(historico, janela=50):
    contador = Counter()
    for jogo in historico[-janela:]:
        contador.update(jogo)
    return contador


def atraso_dezenas(historico):
    atraso = {i: 0 for i in range(1, 26)}

    for dezena in range(1, 26):
        for i, jogo in enumerate(reversed(historico), 1):
            if dezena in jogo:
                atraso[dezena] = i
                break

    return atraso


def metricas_estruturais(jogo):
    pares = sum(1 for n in jogo if n % 2 == 0)
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
        "impares": 15 - pares,
        "soma": soma,
        "blocos": blocos,
    }