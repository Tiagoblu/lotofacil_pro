from core.database import criar_tabelas
from interface.interface import iniciar_interface


def main():
    criar_tabelas()
    iniciar_interface()


if __name__ == "__main__":
    main()