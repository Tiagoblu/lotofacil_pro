import sqlite3

DB_PATH = "database/lotofacil.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Iniciando migração...")

# 1. Criar nova tabela
cursor.execute("""
    CREATE TABLE IF NOT EXISTS concursos_novo (
        numero INTEGER PRIMARY KEY,
        data TEXT,
        d1 INTEGER, d2 INTEGER, d3 INTEGER, d4 INTEGER, d5 INTEGER,
        d6 INTEGER, d7 INTEGER, d8 INTEGER, d9 INTEGER, d10 INTEGER,
        d11 INTEGER, d12 INTEGER, d13 INTEGER, d14 INTEGER, d15 INTEGER
    )
""")

# 2. Buscar dados antigos
cursor.execute("SELECT concurso, data_sorteio, dezenas FROM concursos")
registros = cursor.fetchall()

print(f"Registros encontrados: {len(registros)}")

for concurso, data_sorteio, dezenas in registros:
    lista = [int(x) for x in dezenas.split(",")]

    cursor.execute("""
        INSERT OR IGNORE INTO concursos_novo (
            numero, data,
            d1, d2, d3, d4, d5,
            d6, d7, d8, d9, d10,
            d11, d12, d13, d14, d15
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (concurso, data_sorteio, *lista))

conn.commit()

# 3. Remover tabela antiga
cursor.execute("DROP TABLE concursos")

# 4. Renomear nova
cursor.execute("ALTER TABLE concursos_novo RENAME TO concursos")

conn.commit()
conn.close()

print("Migração concluída com sucesso.")