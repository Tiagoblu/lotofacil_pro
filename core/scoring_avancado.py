from collections import Counter


def calcular_frequencia(concursos):

    freq = Counter()

    for c in concursos:
        for d in c.dezenas:
            freq[d] += 1

    return freq


def calcular_pares_impares(jogo):

    pares = sum(1 for d in jogo if d % 2 == 0)
    impares = 15 - pares

    equilibrio = 7 <= pares <= 8

    return equilibrio


def calcular_equilibrio_faixa(jogo):

    baixa = sum(1 for d in jogo if d <= 13)
    alta = 15 - baixa

    return 6 <= baixa <= 9


def similaridade(jogo, dezenas):

    return len(set(jogo) & set(dezenas))


def pontuar_jogo(jogo, concursos, freq):

    score = 0

    # peso frequência
    for d in jogo:
        score += freq[d]

    # peso histórico
    peso = 1

    for concurso in reversed(concursos):

        acertos = similaridade(jogo, concurso.dezenas)

        score += acertos * peso

        peso *= 0.997

    # penalizar jogos muito parecidos
    for concurso in concursos[-50:]:

        acertos = similaridade(jogo, concurso.dezenas)

        if acertos >= 13:
            score -= 1000

    # bônus equilíbrio pares/ímpares
    if calcular_pares_impares(jogo):
        score += 300

    # bônus distribuição faixa
    if calcular_equilibrio_faixa(jogo):
        score += 300

    return score


def pontuar_jogos(jogos, concursos):

    freq = calcular_frequencia(concursos)

    resultado = []

    for jogo in jogos:

        score = pontuar_jogo(jogo, concursos, freq)

        resultado.append({
            "jogo": jogo,
            "score": score
        })

    resultado.sort(key=lambda x: x["score"], reverse=True)

    return resultado