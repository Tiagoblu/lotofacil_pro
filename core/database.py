import sqlite3

DB_NAME = "lotofacil.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursos (
            data TEXT,
            dezenas TEXT
        )
    """)

    conn.commit()
    conn.close()


def inserir_concurso(numero, data, dezenas):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO concursos (data, dezenas)
        VALUES (?, ?)
    """, (data, dezenas))

    conn.commit()
    conn.close()


def obter_todos_concursos():
    conn = conectar()
    cursor = conn.cursor()

    # usa rowid para ordenação segura
    cursor.execute("SELECT dezenas FROM concursos ORDER BY rowid ASC")
    resultados = cursor.fetchall()

    conn.close()

    return resultados