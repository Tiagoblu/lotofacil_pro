import json
import os
from collections import Counter


def carregar_dados_locais():
    if not os.path.exists("historico.json"):
        print("❌ Arquivo historico.json não encontrado.")
        return None
    
    with open("historico.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    return dados


def analisar_sem_baixar():
    dados = carregar_dados_locais()
    
    if not dados:
        return
    
    print("\n📊 Rodando análise com dados locais...\n")
    
    contador = Counter()

    for concurso in dados:
        for dezena in concurso["listaDezenas"]:
            contador[int(dezena)] += 1

    print("🔥 Top 15 dezenas mais frequentes:\n")
    
    for numero, freq in contador.most_common(15):
        print(f"Número {numero} apareceu {freq} vezes")
