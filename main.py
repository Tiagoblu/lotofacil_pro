# main.py

from infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine
from core.ia.analise_inteligente import AnaliseInteligente
from core.engine.diversificador_adaptativo import DiversificadorAdaptativo


def main():

    print("==== LotoFácil Pro V8 ====\n")

    modo_diversificado = True
    candidatos = 100
    jogos_finais = 5

    print("Atualizando banco...")
    concursos = ConcursoRepository.obter_todos()
    print("Banco já está atualizado.\n")

    print(f"Total de concursos: {len(concursos)}\n")

    print("Gerando candidatos com Motor Probabilístico...\n")

    jogos_motor = ProbabilisticEngine.gerar_jogos(
        concursos,
        quantidade=candidatos
    )

    jogos_formatados = [
        (tuple(jogo.dezenas), score)
        for jogo, score in jogos_motor
    ]

    print("Executando Análise Inteligente...\n")

    analise = AnaliseInteligente.analisar(jogos_formatados, concursos)

    if modo_diversificado:
        print("Aplicando Diversificação Adaptativa V8...\n")
        analise = DiversificadorAdaptativo.selecionar(
            analise,
            quantidade_final=jogos_finais
        )
    else:
        analise = analise[:jogos_finais]

    print("Jogos Finais:\n")

    for i, item in enumerate(analise, 1):

        dezenas = " ".join(f"{n:02d}" for n in item["jogo"])

        print(f"Jogo {i}: {dezenas}")
        print(f"Score: {round(item['score_original'], 6)}")
        print(f"Perfil Detectado: {item['perfil_detectado']}")
        print(f"Nível de Risco: {item['nivel_risco']}")
        print("-" * 60)


if __name__ == "__main__":
    main()