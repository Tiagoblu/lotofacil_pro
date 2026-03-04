# calibrar_modelo.py

from infrastructure.database.repository import ConcursoRepository
from core.statistics.historic_analyzer import HistoricAnalyzer


def main():
    print("Iniciando calibração estatística...\n")

    concursos = ConcursoRepository.obter_todos()

    resultado = HistoricAnalyzer.analisar(concursos)

    print("📊 RESULTADO DA CALIBRAÇÃO\n")
    print(f"Média da soma...........: {resultado['media_soma']}")
    print(f"Desvio padrão da soma...: {resultado['desvio_soma']}")
    print()
    print(f"Média de pares..........: {resultado['media_pares']}")
    print(f"Desvio padrão de pares..: {resultado['desvio_pares']}")
    print("\nCalibração concluída.")


if __name__ == "__main__":
    main()