from collections import Counter
from core.database import obter_todos_concursos


def gerar_frequencia_real():

    resultados = obter_todos_concursos()

    contador = Counter()

    for linha in resultados:

        if not linha:
            continue

        dezenas_brutas = linha[0]

        if not dezenas_brutas:
            continue

        # aceita formato com vírgula ou espaço
        dezenas_str = dezenas_brutas.replace(",", " ").split()

        try:
            dezenas = [int(d) for d in dezenas_str]
            contador.update(dezenas)
        except ValueError:
            continue

    return contador