import requests
import json
import sqlite3
import os

# ===========================
# Configurações
# ===========================
DB_PATH = "lotofacil.db"
JSON_PATH = "historico.json"

# ===========================
# Criar banco
# ===========================
def criar_banco():
    """
    Cria a tabela de concursos no banco.
    Concurso é chave primária para evitar duplicação.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursos (
            concurso INTEGER PRIMARY KEY,
            data_sorteio TEXT,
            dezenas TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Banco criado ou já existente.")

# ===========================
# Pegar último concurso já no banco
# ===========================
def ultimo_concurso_no_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(concurso) FROM concursos")
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado or 0  # se nada no banco, retorna 0

# ===========================
# Inserir no banco
# ===========================
def inserir_no_banco(concursos):
    """
    Insere concursos no banco, ignorando duplicados.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    novos = 0
    for c in concursos:
        dezenas = ",".join(c["listaDezenas"])
        try:
            cursor.execute("""
                INSERT INTO concursos (concurso, data_sorteio, dezenas)
                VALUES (?, ?, ?)
            """, (c["numero"], c["dataApuracao"], dezenas))
            novos += 1
        except sqlite3.IntegrityError:
            continue

    conn.commit()
    conn.close()
    print(f"{novos} concursos novos inseridos no banco.")

# ===========================
# Baixar concursos novos
# ===========================
def baixar_dados_novos():
    """
    Baixa apenas os concursos que ainda não estão no banco.
    Atualiza JSON com todos os concursos baixados anteriormente + novos.
    """
    criar_banco()
    ultimo_banco = ultimo_concurso_no_banco()
    print(f"Último concurso no banco: {ultimo_banco}")

    # 1️⃣ Pegar último concurso da API
    url_ultimo = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
    resp = requests.get(url_ultimo)
    if resp.status_code != 200:
        print("Erro ao acessar API principal.")
        return []
    
    ultimo_concurso_api = resp.json()["numero"]
    print(f"Último concurso disponível: {ultimo_concurso_api}")

    # 2️⃣ Determinar quais concursos baixar
    if ultimo_concurso_api <= ultimo_banco:
        print("Nenhum concurso novo para baixar.")
        return []

    concursos_novos = []
    for c in range(ultimo_banco + 1, ultimo_concurso_api + 1):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{c}"
        r = requests.get(url)
        if r.status_code == 200:
            concursos_novos.append(r.json())
            print(f"Concurso {c} baixado.")
        else:
            print(f"Erro ao baixar concurso {c}")

    # 3️⃣ Atualizar JSON
    todos_dados = []
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            todos_dados = json.load(f)
    
    todos_dados.extend(concursos_novos)  # adiciona apenas os novos
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(todos_dados, f, ensure_ascii=False, indent=4)

    print(f"JSON atualizado com {len(concursos_novos)} novos concursos.")

    # 4️⃣ Inserir no banco
    inserir_no_banco(concursos_novos)

    return concursos_novos
