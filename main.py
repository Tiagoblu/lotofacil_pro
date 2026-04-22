import os
import sys
import sqlite3
import requests
import time

# 1. Configurações de Caminho e Endpoints
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
URL_BASE = "https://servicebus2.caixa.gov.br/portalloterias/api/lotofacil/"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from core.infrastructure.database.database import get_connection
    from core.engine.probabilistic_engine import ProbabilisticEngine
    from core.domain.models import Concurso
except ImportError as e:
    print(f"\n[ERRO DE ESTRUTURA]: {e}")
    sys.exit(1)

def baixar_e_salvar_novos_concursos():
    """
    Sincroniza o banco local. 
    Melhoria: Validação rigorosa de payload para evitar falsos positivos de 'atualizado'.
    """
    print("🔄 Sincronizando com a API da Caixa...")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(numero) FROM concursos")
    resultado = cursor.fetchone()
    ultimo_local = resultado[0] if resultado and resultado[0] is not None else 0
    conn.close()

    proximo = ultimo_local + 1
    novos_cont = 0
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        url = f"{URL_BASE}{proximo}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            # Se a API não responder com sucesso ou demorar, interrompe
            if response.status_code != 200:
                break
            
            dados = response.json()
            
            # Validação crucial: Verifica se as dezenas existem e são 15
            lista_dezenas = dados.get("listaDezenas")
            if not lista_dezenas or len(lista_dezenas) != 15:
                # Se não encontrou dezenas para o próximo, o banco está realmente no limite
                break
            
            dezenas = [int(d) for d in lista_dezenas]
            data_apuracao = dados.get("dataApuracao", "")

            # Persistência atômica
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO concursos 
                (numero, data, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (proximo, data_apuracao, *dezenas))
            conn.commit()
            conn.close()
            
            novos_cont += 1
            proximo += 1
        except Exception as e:
            # Em caso de erro de rede ou JSON, interrompe a tentativa atual
            break
            
    if novos_cont > 0:
        print(f"✅ Sucesso: {novos_cont} novos concursos integrados ao banco.")
    else:
        print(f"ℹ️  Base local no limite (Último: {ultimo_local}). Aguardando novo sorteio oficial.")
    
    return proximo - 1

def preparar_concursos():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM concursos ORDER BY numero ASC")
        rows = cursor.fetchall()
        return [Concurso(numero=r[0], data=r[1], dezenas=tuple(r[2:17])) for r in rows]
    except Exception as e:
        print(f"[ERRO CRÍTICO DB]: {e}")
        return []
    finally:
        conn.close()

def main():
    print("="*65)
    print("       LOTOFÁCIL PRO V11 – Inteligência de Decisão")
    print("="*65)

    try:
        # 1. Atualização Forçada da Base de Dados
        baixar_e_salvar_novos_concursos()

        # 2. Re-carregamento dos dados após sincronização
        lista_concursos = preparar_concursos()
        if not lista_concursos:
            print("[ERRO]: Banco de dados inacessível ou vazio.")
            return

        ultimo_concurso = lista_concursos[-1]
        alvo = ultimo_concurso.numero + 1

        # 3. Execução do Motor de Análise
        engine = ProbabilisticEngine()
        jogos_brutos, info_ciclo = engine.gerar_jogos(
            concursos=lista_concursos, 
            quantidade=5, 
            modo="HIBRIDO_V9"
        )

        # 4. Interface de Decisão
        faltantes = info_ciclo.get('dezenas_faltantes', [])
        score_lider = jogos_brutos[0][1]
        
        if 0 < len(faltantes) <= 4 and score_lider >= 1.18:
            status = "🔥 JANELA DE OURO"
        elif len(faltantes) <= 6:
            status = "✅ OPORTUNIDADE ALTA"
        else:
            status = "⚖️ ESTÁVEL"

        print(f"STATUS DA ESTRATÉGIA : {status}")
        print("-" * 65)
        print(f"Último Registrado: {ultimo_concurso.numero}  |  Alvo: {alvo}")
        print(f"Faltantes no Ciclo: {' '.join(map(str, faltantes))}")
        print("-" * 65)

        print(f"\nJOGOS SUGERIDOS PARA O CONCURSO {alvo}:")
        for i, (jogo_obj, score, rep) in enumerate(jogos_brutos, 1):
            dezenas_fmt = " ".join(f"{d:02d}" for d in sorted(jogo_obj.dezenas))
            print(f"Jogo {i}: {dezenas_fmt} | Score: {score:.6f}")

        # 5. Registro de Histórico (Regra de Ouro)
        engine.salvar_historico_v10(jogos_brutos, alvo=alvo)
        print(f"\n[OK] Jogos salvos na raiz em 'historico_v10.txt'.")

    except Exception as e:
        print(f"\n[FALHA DE EXECUÇÃO]: {e}")

if __name__ == "__main__":
    main()