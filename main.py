# main.py

from infrastructure.database.database import inicializar_banco
from services.geracao_service import GeracaoService


def main():

    print("==== LotoFácil Pro ====\n")

    # Inicializa banco
    inicializar_banco()
    print("Banco inicializado com sucesso.\n")

    # Geração de jogos
    jogos = GeracaoService.gerar_jogos(
        quantidade=5,
        candidatos=500
    )

    if not jogos:
        print("Nenhum jogo gerado.")
        return

    print("Jogos Gerados:\n")

    for i, (jogo, score) in enumerate(jogos, start=1):
        numeros = " ".join(f"{n:02d}" for n in jogo)
        print(f"Jogo {i}: {numeros} | Score: {score:.4f}")


if __name__ == "__main__":
    main()