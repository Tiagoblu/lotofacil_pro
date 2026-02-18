from baixar import baixar_concursos
from analise import analisar_frequencia
from estrategia import gerar_jogo_mais_frequentes


def pedir_intervalo():
    while True:
        try:
            inicio = int(input("Concurso inicial: "))
            fim = int(input("Concurso final: "))

            if inicio <= 0 or fim <= 0:
                print("Os números devem ser positivos.")
                continue

            if inicio > fim:
                print("O concurso inicial não pode ser maior que o final.")
                continue

            return inicio, fim

        except ValueError:
            print("Digite apenas números válidos.")


def menu():
    while True:
        print("\n===== SISTEMA LOTOFÁCIL =====")
        print("1 - Baixar concursos")
        print("2 - Analisar frequência")
        print("3 - Gerar jogo estratégico")
        print("4 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            inicio, fim = pedir_intervalo()
            baixar_concursos(inicio, fim)

        elif opcao == "2":
            try:
                contador = analisar_frequencia()
                print("\nFrequência dos números:")
                for numero in range(1, 26):
                    print(f"{numero}: {contador[numero]}")
            except FileNotFoundError:
                print("Histórico não encontrado. Baixe concursos primeiro.")

        elif opcao == "3":
            try:
                contador = analisar_frequencia()
                jogo = gerar_jogo_mais_frequentes(contador)
                print("\nSugestão estratégica:")
                print(jogo)
            except FileNotFoundError:
                print("Histórico não encontrado. Baixe concursos primeiro.")

        elif opcao == "4":
            print("Encerrando sistema...")
            break

        else:
            print("Opção inválida. Escolha entre 1 e 4.")


if __name__ == "__main__":
    menu()
