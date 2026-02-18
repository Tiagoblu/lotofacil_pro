import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "lotofacil.db")

def criar_banco():

    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concurso INTEGER UNIQUE,
            data_sorteio TEXT,
            dezenas TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("Banco criado com sucesso.")
