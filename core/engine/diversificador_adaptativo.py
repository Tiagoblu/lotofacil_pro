# core/engine/diversificador_adaptativo.py

class DiversificadorAdaptativo:

    LIMITE_CLONE = 12
    LIMITE_PENALIZACAO = 9
    FATOR_PENALIZACAO = 0.3

    @staticmethod
    def selecionar(jogos_analise, quantidade_final=5):

        selecionados = []

        candidatos = sorted(
            jogos_analise,
            key=lambda x: x["score_original"],
            reverse=True
        )

        while candidatos and len(selecionados) < quantidade_final:

            melhor = None
            melhor_score_ajustado = -999999

            for candidato in candidatos:

                descartar = False
                penalidade_total = 0

                for escolhido in selecionados:

                    intersecao = len(
                        set(candidato["jogo"]) &
                        set(escolhido["jogo"])
                    )

                    # 1️⃣ Clone excessivo → descarta
                    if intersecao > DiversificadorAdaptativo.LIMITE_CLONE:
                        descartar = True
                        break

                    # 2️⃣ Penalização leve
                    if intersecao >= DiversificadorAdaptativo.LIMITE_PENALIZACAO:
                        penalidade = (
                            (intersecao / 15)
                            * DiversificadorAdaptativo.FATOR_PENALIZACAO
                        )
                        penalidade_total += penalidade

                if descartar:
                    continue

                score_ajustado = candidato["score_original"] - penalidade_total

                if score_ajustado > melhor_score_ajustado:
                    melhor_score_ajustado = score_ajustado
                    melhor = candidato

            if melhor is None:
                break

            selecionados.append(melhor)
            candidatos.remove(melhor)

        return selecionados