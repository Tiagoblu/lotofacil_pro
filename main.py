# main.py

from infrastructure.database.repository import ConcursoRepository
from infrastructure.downloader.baixar import baixar_dados_novos
from core.engine.motor_jogos import selecionar_melhores_jogos


def main():

    print("==== LotoFácil Pro ====\n")

    print("Atualizando banco...")

    ok, msg = baixar_dados_novos()

    print(msg)

    concursos = ConcursoRepository.obter_todos()

    print("\nTotal de concursos:", len(concursos))

    print("\nGerando jogos...\n")

    melhores = selecionar_melhores_jogos(concursos, 5)

    print("Jogos Gerados:\n")

    for i, r in enumerate(melhores, 1):

        jogo = " ".join(f"{d:02d}" for d in r["jogo"])

        print(f"Jogo {i}: {jogo} | Score: {r['score']}")


if __name__ == "__main__":
    main()