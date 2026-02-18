import sqlite3
import os
from collections import Counter

from core.estrategia import gerar_jogo


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "lotofacil.db")


def gerar_simulacao(nivel="A", quantidade=1):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT dezenas FROM concursos")
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        return ["❌ Nenhum dado encontrado no banco."]

    frequencia = Counter()

    for linha in resultados:
        dezenas = linha[0].split(",")
        for dezena in dezenas:
            frequencia[int(dezena)] += 1

    jogos = []

    for _ in range(quantidade):
        jogo = gerar_jogo(frequencia, nivel)
        jogos.append(jogo)

    # Formatação para exibição
    resultado_formatado = [f"🎯 SIMULAÇÃO - Nível {nivel}"]
    resultado_formatado.append("")

    for i, jogo in enumerate(jogos, 1):
        linha = " ".join(f"{n:02d}" for n in jogo)
        resultado_formatado.append(f"Jogo {i}: {linha}")

    return resultado_formatado
