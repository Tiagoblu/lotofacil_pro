import requests
import sqlite3
import os
import re
from pathlib import Path
from datetime import datetime

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine

DB_PATH = Path("database/lotofacil.db")
URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
HISTORICO_PATH = "historico_v10.txt"

# ----------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------
def obter_ultimo_concurso_local() -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero) FROM concursos")
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado[0] else 0

def obter_set_concursos_no_txt() -> set:
    """Escaneia o arquivo inteiro e retorna um SET com todos os números de concursos processados."""
    if not os.path.exists(HISTORICO_PATH):
        return set()
    try:
        with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # Busca todos os números após "Concurso conferido: "
            matches = re.findall(r"Concurso conferido: (\d+)", conteudo)
            return {int(m) for m in matches}
    except Exception:
        return set()

def baixar_e_salvar_novos_concursos():
    ultimo_local = obter_ultimo_concurso_local()
    proximo = ultimo_local + 1
    novos = 0
    while True:
        url = URL_BASE + str(proximo)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200: break
            dados = response.json()
            lista_dezenas = dados.get("listaDezenas", [])
            if len(lista_dezenas) != 15: break
            dezenas = [int(d) for d in lista_dezenas]
            data = dados.get("dataApuracao", "")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO concursos
                (numero, data, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (proximo, data, *dezenas))
            conn.commit()
            conn.close()
            novos += 1
            proximo += 1
        except Exception: break
    return novos, proximo - 1

def contar_acertos(jogo_dezenas, dezenas_sorteadas) -> int:
    return len(set(jogo_dezenas) & set(dezenas_sorteadas))

def carregar_jogos_v9() -> list:
    caminho = "jogos_v9_fixos.txt"
    jogos = []
    if os.path.exists(caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                for linha in f:
                    dezenas = [int(x) for x in linha.replace(',', ' ').split() if x.isdigit()]
                    if len(dezenas) >= 15: jogos.append(dezenas[:15])
        except Exception: pass
    if not jogos:
        jogos = [[2, 3, 4, 6, 7, 10, 12, 15, 16, 19, 20, 21, 22, 23, 24], 
                 [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 18, 20, 22, 24, 25]]
    return jogos

def salvar_historico_v10(ultimo_concurso_db, dezenas_sorteadas, jogos_motor):
    linha_div = "-" * 80
    with open(HISTORICO_PATH, "a", encoding="utf-8") as f:
        f.write(f"{linha_div}\n")
        f.write(f"Execução em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Concurso conferido: {ultimo_concurso_db.numero}\n")
        f.write("Resultado: " + " ".join(f"{d:02d}" for d in sorted(dezenas_sorteadas)) + "\n\n")
        for idx, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
            dezenas_jogo = sorted(jogo.dezenas)
            acertos = contar_acertos(dezenas_jogo, dezenas_sorteadas)
            dezenas_acertadas = sorted(set(dezenas_jogo) & set(dezenas_sorteadas))
            f.write(f"Jogo {idx}: {' '.join(f'{d:02d}' for d in dezenas_jogo)}\n")
            f.write(f"  Score V10             : {score:.6f}\n")
            f.write(f"  Repetições Anteriores : {repeticoes}\n")
            f.write(f"  Acertos               : {acertos}\n")
            f.write("  Dezenas acertadas      : " + " ".join(f"{d:02d}" for d in dezenas_acertadas) + "\n\n")

def processar_concurso(concurso_obj, todos_concursos, jogos_v9):
    historico_visivel = [c for c in todos_concursos if c.numero < concurso_obj.numero]
    if not historico_visivel: return
    jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
        historico_visivel, quantidade=5, candidatos=300, modo="HIBRIDO_V9", jogos_base=jogos_v9
    )
    salvar_historico_v10(concurso_obj, list(concurso_obj.dezenas), jogos_motor)

# ----------------------------------------------------------------------
# Função principal
# ----------------------------------------------------------------------
def main():
    print("="*60)
    print("==== LotoFácil Pro V10 – Motor Estrutural Adaptativo ====")
    print("="*60 + "\n")

    inicializar_banco()
    baixar_e_salvar_novos_concursos()
    
    concursos = ConcursoRepository.obter_todos()
    if not concursos: return

    # --- NOVA LÓGICA DE SCANNER TOTAL ---
    concursos_processados = obter_set_concursos_no_txt()
    concursos_no_banco = [c.numero for c in concursos]
    
    # Identifica concursos que estão no banco mas não estão no TXT
    faltantes = sorted([n for n in concursos_no_banco if n not in concursos_processados])

    if faltantes:
        print(f"[AVISO] Buracos detectados no histórico! Recompondo {len(faltantes)} concurso(s)...")
        jogos_v9 = carregar_jogos_v9()
        for num in faltantes:
            conc_atual = next((c for c in concursos if c.numero == num), None)
            if conc_atual:
                print(f"  > Sincronizando Concurso {num}...")
                processar_concurso(conc_atual, concursos, jogos_v9)
        print("[OK] Histórico 100% integrado.\n")
    else:
        print("[INFO] Histórico de conferências está íntegro.\n")

    # --- GERAÇÃO DO PRÓXIMO ---
    ultimo_db = concursos[-1]
    jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
        concursos, quantidade=5, candidatos=300, modo="HIBRIDO_V9", jogos_base=carregar_jogos_v9()
    )

    faltantes_ciclo = info_ciclo.get('dezenas_faltantes', [])
    print(f"Último no banco: {ultimo_db.numero} | Status do Ciclo: {info_ciclo.get('ciclo', 'N/A')}")
    print(f"Faltantes ({len(faltantes_ciclo)}): {' '.join(f'{d:02d}' for d in faltantes_ciclo)}")
    
    if 0 < len(faltantes_ciclo) <= 5:
        print("!!! ALERTA: FECHAMENTO DE CICLO IMINENTE !!!")

    print("\nJOGOS PARA O PRÓXIMO CONCURSO:")
    for i, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
        print(f"Jogo {i}: {' '.join(f'{n:02d}' for n in sorted(jogo.dezenas))} | Score: {score:.6f}")

if __name__ == "__main__":
    main()