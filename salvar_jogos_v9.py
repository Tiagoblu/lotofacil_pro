# salvar_jogos_v9.py

from pathlib import Path

def main():
    # Jogos fixos do V9 (extraídos das suas prints)
    jogos_v9 = {
        "Jogo A": [2, 3, 4, 6, 7, 10, 12, 15, 16, 19, 20, 21, 22, 23, 24],
        "Jogo B": [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 18, 20, 22, 24, 25],
        "Jogo C": [2, 3, 5, 6, 8, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24],
        "Jogo D": [2, 5, 7, 8, 9, 11, 13, 14, 15, 17, 20, 21, 23, 24, 25],
    }

    caminho = Path("jogos_v9_fixos.txt")
    with caminho.open("w", encoding="utf-8") as f:
        f.write("Jogos fixos do V9 (histórico do Tiago)\n")
        f.write("=" * 40 + "\n\n")
        for nome, dezenas in jogos_v9.items():
            linha = " ".join(f"{d:02d}" for d in dezenas)
            f.write(f"{nome}: {linha}\n")

    print(f"Arquivo salvo em: {caminho.resolve()}")


if __name__ == "__main__":
    main()