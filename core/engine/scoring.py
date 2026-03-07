# core/scoring_avancado.py

def calcular_penalizacao_sequencia(jogo):
    jogo_ordenado = sorted(jogo)
    maior_seq = 1
    seq_atual = 1

    for i in range(1, len(jogo_ordenado)):
        if jogo_ordenado[i] == jogo_ordenado[i - 1] + 1:
            seq_atual += 1
            maior_seq = max(maior_seq, seq_atual)
        else:
            seq_atual = 1

    # Penalização progressiva suave
    if maior_seq >= 10:
        return 0.75
    elif maior_seq >= 8:
        return 0.85
    elif maior_seq >= 6:
        return 0.92
    else:
        return 1.0


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

    # Penalização estrutural por sequência longa
    penalidade = calcular_penalizacao_sequencia(jogo)
    score = score * penalidade

    return score