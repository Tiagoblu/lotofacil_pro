import requests
import sqlite3
import os
import shutil
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "lotofacil.db")
BACKUP_PATH = os.path.join(BASE_DIR, "database", "backup_lotofacil.db")

URL_API = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

cancelar_download = False


def solicitar_cancelamento():
    global cancelar_download
    cancelar_download = True


def criar_backup():
    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, BACKUP_PATH)


def obter_ultimo_concurso():
    if not os.path.exists(DB_PATH):
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursos (
            concurso INTEGER PRIMARY KEY,
            dezenas TEXT
        )
    """)

    cursor.execute("SELECT MAX(concurso) FROM concursos")
    resultado = cursor.fetchone()[0]
    conn.close()

    return resultado if resultado else 0


def salvar_concurso(numero, dezenas):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO concursos (concurso, dezenas)
        VALUES (?, ?)
    """, (numero, dezenas))

    conn.commit()
    conn.close()


def baixar_dados_novos(callback_progresso=None):

    global cancelar_download
    cancelar_download = False

    criar_backup()

    ultimo = obter_ultimo_concurso()

    tentativa_max = 3

    try:
        response = requests.get(URL_API, timeout=10)
        response.raise_for_status()
        total_atual = response.json()["numero"]
    except:
        return False, "Erro ao conectar com API."

    if ultimo == total_atual:
        return True, "Banco já está atualizado."

    total_para_baixar = total_atual - ultimo
    baixados = 0

    for numero in range(ultimo + 1, total_atual + 1):

        if cancelar_download:
            return False, "Download cancelado pelo usuário."

        sucesso = False

        for tentativa in range(tentativa_max):
            try:
                r = requests.get(f"{URL_API}/{numero}", timeout=10)
                r.raise_for_status()
                dados = r.json()

                dezenas = ",".join(dados["listaDezenas"])
                salvar_concurso(numero, dezenas)

                sucesso = True
                break
            except:
                time.sleep(1)

        if not sucesso:
            return False, f"Falha ao baixar concurso {numero}"

        baixados += 1
        percentual = int((baixados / total_para_baixar) * 100)

        if callback_progresso:
            callback_progresso(percentual, numero)

    return True, "Download concluído com sucesso."
