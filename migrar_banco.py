# migrar_banco.py

import requests
import sqlite3
from pathlib import Path

DB_PATH = Path("database/lotofacil.db")
URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"


def obter_ultimo_concurso_local():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero) FROM concursos")
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado[0] else 0


def baixar_concurso(numero: int):
    url = URL_BASE + str(numero)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"  Erro ao buscar concurso {numero}: {e}")
        return None


def salvar_concurso(dados: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    numero = dados.get("numero")
    data = dados.get("dataApuracao", "")

    lista_dezenas = dados.get("listaDezenas", [])
    if len(lista_dezenas) != 15:
        print(f"  Concurso {numero} com dezenas inválidas, pulando.")
        conn.close()
        return False

    dezenas = [int(d) for d in lista_dezenas]

    cursor.execute("""
        INSERT OR IGNORE INTO concursos
        (numero, data, d1, d2, d3, d4, d5, d6, d7, d8,
         d9, d10, d11, d12, d13, d14, d15)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (numero, data, *dezenas))

    conn.commit()
    conn.close()
    return True


def main():
    print("Iniciando migração...\n")

    ultimo_local = obter_ultimo_concurso_local()
    print(f"Último concurso no banco local: {ultimo_local}")

    proximo = ultimo_local + 1
    novos = 0

    while True:
        print(f"  Buscando concurso {proximo}...")
        dados = baixar_concurso(proximo)

        if dados is None:
            print(f"  Concurso {proximo} não disponível ainda na API. Encerrando.")
            break

        sucesso = salvar_concurso(dados)
        if sucesso:
            print(f"  Concurso {proximo} salvo com sucesso.")
            novos += 1
            proximo += 1
        else:
            break

    print(f"\nMigração concluída. {novos} novo(s) concurso(s) adicionado(s).")


if __name__ == "__main__":
    main()