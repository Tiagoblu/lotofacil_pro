# main.py

import requests
import sqlite3
from pathlib import Path

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine

DB_PATH = Path("database/lotofacil.db")
URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"


def obter_ultimo_concurso_local():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero) FROM concursos")
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado[0] else 0


def baixar_e_salvar_novos_concursos():
    ultimo_local = obter_ultimo_concurso_local()
    proximo = ultimo_local + 1
    novos = 0

    while True:
        url = URL_BASE + str(proximo)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                break

            dados = response.json()
            lista_dezenas = dados.get("listaDezenas", [])

            if len(lista_dezenas) != 15:
                break

            dezenas = [int(d) for d in lista_dezenas]
            data = dados.get("dataApuracao", "")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO concursos
                (numero, data, d1, d2, d3, d4, d5, d6, d7, d8,
                 d9, d10, d11, d12, d13, d14, d15)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (proximo, data, *dezenas))
            conn.commit()
            conn.close()

            novos += 1
            proximo += 1

        except Exception:
            break

    return novos, proximo - 1


def main():
    print("==== LotoFácil Pro V10 – Motor Estrutural Adaptativo ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    print("Verificando novos concursos na API...")
    novos, ultimo = baixar_e_salvar_novos_concursos()
    if novos > 0:
        print(f"{novos} novo(s) concurso(s) baixado(s). Último: {ultimo}\n")
    else:
        print(f"Banco já atualizado. Último concurso: {ultimo}\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos: {len(concursos)}\n")

    print("Gerando candidatos com Motor Probabilístico...\n")

    modo_estrategia = "BALANCEADO"

    jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
        concursos,
        quantidade=5,
        candidatos=300,
        modo=modo_estrategia
    )

    print(f"Modo Estratégico Ativo : {modo_estrategia}")
    print(f"Ciclo Detectado (V10)  : {info_ciclo['ciclo']}")
    print(f"Índice de Volatilidade : {info_ciclo['indice_volatilidade']:.4f}")
    print(f"Peso Recência          : {info_ciclo['peso_recencia']:.2f}")
    print()
    print("Jogos Finais:\n")

    for i, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
        dezenas_formatadas = " ".join(f"{n:02d}" for n in jogo.dezenas)

        print(f"Jogo {i}: {dezenas_formatadas}")
        print(f"Score V10             : {score:.6f}")
        print(f"Repetições Anteriores : {repeticoes}")
        print("-" * 60)


if __name__ == "__main__":
    main()