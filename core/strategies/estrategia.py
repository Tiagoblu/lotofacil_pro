import random


def gerar_jogo(nivel="C"):
    """
    Geração com leve viés probabilístico.
    Números centrais levemente favorecidos.
    """

    universo = list(range(1, 26))

    if nivel == "A":
        return sorted(random.sample(universo, 15))

    if nivel == "B":
        pesos = [1 + (i in range(8, 18)) for i in universo]
    elif nivel == "C":
        pesos = [1 + (i in range(5, 21)) for i in universo]
    else:  # D
        pesos = [2 if 10 <= i <= 20 else 1 for i in universo]

    selecionados = random.choices(universo, weights=pesos, k=25)

    jogo = list(set(selecionados))

    while len(jogo) < 15:
        jogo.append(random.choice(universo))

    return sorted(random.sample(jogo, 15))