from baixar import baixar_dados
from analise import analisar_sem_baixar


def menu():
    while True:
        print("\n===== LOTOFÁCIL PRO =====")
        print("1 - Baixar dados da API")
        print("2 - Analisar dados locais (sem baixar)")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            baixar_dados()

        elif opcao == "2":
            analisar_sem_baixar()

        elif opcao == "0":
            print("Encerrando sistema...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
