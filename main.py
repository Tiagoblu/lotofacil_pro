# main.py

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine


def main():
    print("==== LotoFácil Pro V10 – Motor Estrutural Adaptativo ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos: {len(concursos)}\n")

    print("Gerando candidatos com Motor Probabilístico...\n")

    # MODOS DISPONÍVEIS:
    # "CONSERVADOR"
    # "BALANCEADO"
    # "AGRESSIVO"

    modo_estrategia = "BALANCEADO"

    jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
        concursos,
        quantidade=5,
        candidatos=300,
        modo=modo_estrategia
    )

    print(f"Modo Estratégico Ativo : {modo_estrategia}")
    print(f"Ciclo Detectado (V10)  : {info_ciclo['ciclo']}")
    print(f"Índice de Volatilidade : {info_ciclo['indice_volatilidade']:.4f}")
    print(f"Peso Recência          : {info_ciclo['peso_recencia']:.2f}")
    print()
    print("Jogos Finais:\n")

    for i, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
        dezenas_formatadas = " ".join(f"{n:02d}" for n in jogo.dezenas)

        print(f"Jogo {i}: {dezenas_formatadas}")
        print(f"Score V10             : {score:.6f}")
        print(f"Repetições Anteriores : {repeticoes}")
        print("-" * 60)


if __name__ == "__main__":
    main()