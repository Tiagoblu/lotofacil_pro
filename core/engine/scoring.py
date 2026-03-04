def calcular_score(jogo, freq_total, freq_recente, atraso):

    score = 0

    # Frequência histórica
    for dezena in jogo:
        score += freq_total.get(dezena, 0) * 1.0

    # Frequência recente (peso maior)
    for dezena in jogo:
        score += freq_recente.get(dezena, 0) * 1.5

    # Atraso (perfil agressivo)
    for dezena in jogo:
        score += atraso.get(dezena, 0) * 0.8

    pares = sum(1 for n in jogo if n % 2 == 0)
    soma = sum(jogo)

    # Par/ímpar ideal
    if 6 <= pares <= 9:
        score += 15

    # Faixa de soma ideal
    if 170 <= soma <= 230:
        score += 20

    return score