# core/engine/motor_jogos.py

from core.scoring_avancado import pontuar_jogos


def gerar_jogos_base():
    """
    Gera jogos candidatos simples.
    (Depois será substituído por estratégias avançadas)
    """

    jogos = []

    for inicio in range(1, 11):

        jogo = tuple(range(inicio, inicio + 15))

        jogo = tuple(sorted([(d - 1) % 25 + 1 for d in jogo]))

        if len(set(jogo)) == 15:
            jogos.append(jogo)

    return jogos


def selecionar_melhores_jogos(concursos, quantidade=5):

    jogos = gerar_jogos_base()

    pontuados = pontuar_jogos(jogos, concursos)

    pontuados.sort(key=lambda x: x["score"], reverse=True)

    return pontuados[:quantidade]