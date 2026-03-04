# infrastructure/database/database.py

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "database", "lotofacil.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursos (
            numero INTEGER PRIMARY KEY,
            data TEXT,
            d1 INTEGER, d2 INTEGER, d3 INTEGER, d4 INTEGER, d5 INTEGER,
            d6 INTEGER, d7 INTEGER, d8 INTEGER, d9 INTEGER, d10 INTEGER,
            d11 INTEGER, d12 INTEGER, d13 INTEGER, d14 INTEGER, d15 INTEGER
        )
    """)

    conn.commit()
    conn.close()


def inicializar_banco():
    """
    Inicializa o banco garantindo que as tabelas existam.
    """
    criar_tabelas()