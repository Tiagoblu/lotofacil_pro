# core/engine/diversificador_adaptativo.py

class DiversificadorAdaptativo:

    @staticmethod
    def selecionar(jogos_analise, quantidade_final=5):

        """
        jogos_analise = lista de dicts vindos da AnaliseInteligente
        contendo:
            - jogo
            - score_original
            - indice_equilibrio
            - indice_tendencia
        """

        selecionados = []

        # Ordena inicialmente pelo score original
        candidatos = sorted(
            jogos_analise,
            key=lambda x: x["score_original"],
            reverse=True
        )

        while candidatos and len(selecionados) < quantidade_final:

            melhor = None
            melhor_score_ajustado = -999999

            for candidato in candidatos:

                penalidade_total = 0

                for escolhido in selecionados:
                    intersecao = len(
                        set(candidato["jogo"]) &
                        set(escolhido["jogo"])
                    )

                    # Penalização adaptativa
                    peso = 1 - candidato["indice_equilibrio"]
                    penalidade = (intersecao / 15) * peso

                    penalidade_total += penalidade

                score_ajustado = candidato["score_original"] - penalidade_total

                if score_ajustado > melhor_score_ajustado:
                    melhor_score_ajustado = score_ajustado
                    melhor = candidato

            selecionados.append(melhor)
            candidatos.remove(melhor)

        return selecionados