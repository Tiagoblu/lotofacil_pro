import random


def gerar_jogo(contador, nivel="A"):

    numeros_ordenados = [num for num, _ in contador.most_common()]
    todos_numeros = list(contador.keys())

    if nivel == "A":
        # 100% frequência (conservador)
        escolhidos = numeros_ordenados[:15]

    elif nivel == "B":
        # 10 mais frequentes + 5 aleatórios entre os 20 mais frequentes
        base = numeros_ordenados[:10]
        extras_pool = numeros_ordenados[:20]
        extras = random.sample([n for n in extras_pool if n not in base], 5)
        escolhidos = base + extras

    elif nivel == "C":
        # 8 mais frequentes + 7 aleatórios do restante
        base = numeros_ordenados[:8]
        restante = [n for n in todos_numeros if n not in base]
        extras = random.sample(restante, 7)
        escolhidos = base + extras

    elif nivel == "D":
        # 15 totalmente aleatórios (agressivo)
        escolhidos = random.sample(todos_numeros, 15)

    else:
        # fallback segurança
        escolhidos = numeros_ordenados[:15]

    escolhidos.sort()
    return escolhidos
