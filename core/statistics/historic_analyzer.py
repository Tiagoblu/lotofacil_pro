import math


class HistoricAnalyzer:

    @staticmethod
    def analisar(concursos):
        if not concursos:
            raise ValueError("Nenhum concurso disponível para análise.")

        somas = []
        pares = []

        for concurso in concursos:
            dezenas = concurso.dezenas  # já é tupla

            soma = sum(dezenas)
            qtd_pares = sum(1 for d in dezenas if d % 2 == 0)

            somas.append(soma)
            pares.append(qtd_pares)

        media_soma = sum(somas) / len(somas)
        media_pares = sum(pares) / len(pares)

        desvio_soma = math.sqrt(
            sum((x - media_soma) ** 2 for x in somas) / len(somas)
        )

        desvio_pares = math.sqrt(
            sum((x - media_pares) ** 2 for x in pares) / len(pares)
        )

        return {
            "media_soma": round(media_soma, 4),
            "desvio_soma": round(desvio_soma, 4),
            "media_pares": round(media_pares, 4),
            "desvio_pares": round(desvio_pares, 4),
        }