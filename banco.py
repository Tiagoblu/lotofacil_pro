import sqlite3


def criar_banco():
    conexao = sqlite3.connect("lotofacil.db")
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concursos (
        numero INTEGER PRIMARY KEY,
        data TEXT,
        dezenas TEXT
    )
    """)

    conexao.commit()
    conexao.close()

    print("Banco de dados criado com sucesso.")
