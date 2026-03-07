# core/ia/analise_inteligente.py

from statistics import mean


class AnaliseInteligente:

    @staticmethod
    def analisar(jogos, concursos):

        if not jogos or not concursos:
            return []

        # Frequência histórica simples
        frequencia = {n: 0 for n in range(1, 26)}

        for concurso in concursos:
            for dezena in concurso.dezenas:
                frequencia[dezena] += 1

        total_concursos = len(concursos)

        resultados = []

        for jogo, score in jogos:

            soma = sum(jogo)
            pares = sum(1 for n in jogo if n % 2 == 0)
            impares = 15 - pares

            media_freq = mean(frequencia[n] for n in jogo)

            # Índice de equilíbrio (baseado em paridade e soma)
            equilibrio = 1 - abs(pares - 7.5) / 7.5
            equilibrio = round(max(0, min(1, equilibrio)), 3)

            # Índice de tendência (frequência média normalizada)
            tendencia = media_freq / total_concursos
            tendencia = round(max(0, min(1, tendencia)), 3)

            # Detectar perfil estrutural
            if tendencia > 0.65:
                perfil_detectado = "Agressivo"
            elif tendencia < 0.45:
                perfil_detectado = "Conservador"
            else:
                perfil_detectado = "Balanceado"

            # Modo automático híbrido → suaviza para balanceado
            perfil_aplicado = "Balanceado"

            # Nível de risco baseado na combinação
            risco_score = (1 - equilibrio) + abs(tendencia - 0.5)
            if risco_score > 0.8:
                nivel_risco = "Alto"
            elif risco_score > 0.4:
                nivel_risco = "Moderado"
            else:
                nivel_risco = "Controlado"

            # Análise textual híbrida (nível médio)
            analise_textual = (
                f"O jogo apresenta estrutura com {pares} pares e {impares} ímpares, "
                f"soma total de {soma}. O índice de equilíbrio estrutural é {equilibrio}, "
                f"indicando estabilidade estatística moderada. "
                f"A tendência histórica média das dezenas selecionadas é {tendencia}, "
                f"classificando o perfil como {perfil_detectado}. "
                f"O nível de risco estimado é {nivel_risco}, dentro de um modelo híbrido balanceado."
            )

            resultados.append({
                "jogo": jogo,
                "score_original": score,
                "perfil_detectado": perfil_detectado,
                "perfil_aplicado": perfil_aplicado,
                "indice_equilibrio": equilibrio,
                "indice_tendencia": tendencia,
                "nivel_risco": nivel_risco,
                "analise_textual": analise_textual
            })

        return resultados