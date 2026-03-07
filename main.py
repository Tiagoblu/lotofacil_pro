# main.py

from infrastructure.database.repository import ConcursoRepository
from infrastructure.downloader.baixar import baixar_dados_novos
from services.geracao_service import GeracaoService
from core.ia.analise_inteligente import AnaliseInteligente


def main():

    print("==== LotoFácil Pro V7 ====\n")

    print("Atualizando banco...")
    ok, msg = baixar_dados_novos()
    print(msg)

    concursos = ConcursoRepository.obter_todos()
    print("\nTotal de concursos:", len(concursos))

    print("\nGerando jogos com Motor Probabilístico...\n")

    resultados = GeracaoService.gerar_jogos(quantidade=5, candidatos=500)

    if not resultados:
        print("Nenhum jogo gerado.")
        return

    print("Executando Análise Inteligente V7...\n")

    analise = AnaliseInteligente.analisar(resultados, concursos)

    print("Jogos Gerados com Análise:\n")

    for i, item in enumerate(analise, 1):

        jogo = " ".join(f"{d:02d}" for d in item["jogo"])

        print(f"Jogo {i}: {jogo}")
        print(f"Score: {item['score_original']}")
        print(f"Perfil Detectado: {item['perfil_detectado']}")
        print(f"Nível de Risco: {item['nivel_risco']}")
        print(f"Análise IA: {item['analise_textual']}")
        print("-" * 60)


if __name__ == "__main__":
    main()