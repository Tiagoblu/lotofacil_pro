import json
import os
from collections import Counter


def gerar_simulacao():
    if not os.path.exists("historico.json"):
        print("❌ Arquivo historico.json não encontrado.")
        return
    
    with open("historico.json", "r", encoding="utf-8") as f:
        dados = json.load(f)

    contador = Counter()

    for concurso in dados:
        for dezena in concurso["listaDezenas"]:
            contador[int(dezena)] += 1

    mais_frequentes = [numero for numero, _ in contador.most_common(15)]

    mais_frequentes.sort()

    print("\n🎯 JOGO SIMULADO (baseado em frequência):\n")
    
    for numero in mais_frequentes:
        print(f"{numero:02}", end=" ")

    print("\n")
