from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine


def main():
    print("==== LotoFácil Pro V9 ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos: {len(concursos)}\n")

    print("Gerando candidatos com Motor Probabilístico...\n")

    jogos_motor = ProbabilisticEngine.gerar_jogos(
        concursos,
        quantidade=5,
        candidatos=300
    )

    print("\nJogos Finais:\n")

    for i, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
        dezenas_formatadas = " ".join(f"{n:02d}" for n in jogo.dezenas)

        print(f"Jogo {i}: {dezenas_formatadas}")
        print(f"Score: {score:.6f}")
        print(f"Repetições Concurso Anterior: {repeticoes}")
        print("-" * 60)


if __name__ == "__main__":
    main()