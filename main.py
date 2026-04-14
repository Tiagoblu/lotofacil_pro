import requests
import sqlite3
import os
from pathlib import Path
from datetime import datetime

from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.engine.probabilistic_engine import ProbabilisticEngine

DB_PATH = Path("database/lotofacil.db")
URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"

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
            cursor.execute(
                """
                INSERT OR IGNORE INTO concursos
                (numero, data, d1, d2, d3, d4, d5, d6, d7, d8,
                 d9, d10, d11, d12, d13, d14, d15)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (proximo, data, *dezenas),
            )
            conn.commit()
            conn.close()

            novos += 1
            proximo += 1

        except Exception:
            break

    return novos, proximo - 1


def contar_acertos(jogo_dezenas, dezenas_sorteadas) -> int:
    return len(set(jogo_dezenas) & set(dezenas_sorteadas))


def carregar_jogos_v9(caminho: str = "jogos_v9_fixos.txt") -> list:
    jogos = []
    if os.path.exists(caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                for linha in f:
                    dezenas = [int(x) for x in linha.replace(',', ' ').split() if x.isdigit()]
                    if len(dezenas) >= 15:
                        jogos.append(dezenas[:15])
        except Exception as e:
            print(f"Aviso: Erro ao ler {caminho} ({e}). Usando fallback interno.")
            
    if not jogos:
        jogos = [
            [2, 3, 4, 6, 7, 10, 12, 15, 16, 19, 20, 21, 22, 23, 24],
            [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 18, 20, 22, 24, 25],
            [2, 3, 5, 6, 8, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24],
            [2, 5, 7, 8, 9, 11, 13, 14, 15, 17, 20, 21, 23, 24, 25]
        ]
    return jogos


def salvar_historico_v10(
    ultimo_concurso_db,
    dezenas_sorteadas,
    jogos_motor,
    caminho_arquivo: str = "historico_v10.txt",
):
    linha_div = "-" * 80
    with open(caminho_arquivo, "a", encoding="utf-8") as f:
        f.write(f"{linha_div}\n")
        f.write(f"Execução em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Concurso conferido: {ultimo_concurso_db.numero}\n")
        f.write(
            "Resultado: "
            + " ".join(f"{d:02d}" for d in sorted(dezenas_sorteadas))
            + "\n\n"
        )

        for idx, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
            dezenas_jogo = sorted(jogo.dezenas)
            acertos = contar_acertos(dezenas_jogo, dezenas_sorteadas)
            dezenas_acertadas = sorted(set(dezenas_jogo) & set(dezenas_sorteadas))

            f.write(f"Jogo {idx}: {' '.join(f'{d:02d}' for d in dezenas_jogo)}\n")
            f.write(f"  Score V10             : {score:.6f}\n")
            f.write(f"  Repetições Anteriores : {repeticoes}\n")
            f.write(f"  Acertos               : {acertos}\n")
            f.write(
                "  Dezenas acertadas      : "
                + " ".join(f"{d:02d}" for d in dezenas_acertadas)
                + "\n\n"
            )


# ----------------------------------------------------------------------
# Função principal
# ----------------------------------------------------------------------
def main():
    print("="*60)
    print("==== LotoFácil Pro V10 – Motor Estrutural Adaptativo ====")
    print("="*60 + "\n")

    print("[DEBUG] Inicializando banco...")
    inicializar_banco()
    
    novos, ultimo_concurso_numero = baixar_e_salvar_novos_concursos()
    if novos > 0:
        print(f"[API] {novos} novo(s) concurso(s) baixado(s). Último: {ultimo_concurso_numero}\n")
    else:
        print(f"[API] Banco atualizado. Último concurso: {ultimo_concurso_numero}\n")

    concursos = ConcursoRepository.obter_todos()
    if not concursos:
        print("Erro: Nenhum concurso encontrado.")
        return

    ultimo_concurso_db = concursos[-1]
    jogos_v9 = carregar_jogos_v9()
    
    # Execução do Motor
    jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
        concursos,
        quantidade=5,
        candidatos=300,
        modo="HIBRIDO_V9",
        jogos_base=jogos_v9
    )

    # --- DASHBOARD DE CICLO (UI COMERCIAL) ---
    faltantes = info_ciclo.get('dezenas_faltantes', [])
    qtd_faltantes = len(faltantes)
    
    print("="*30)
    print(f"DASHBOARD DO CICLO ATUAL")
    print("="*30)
    print(f"Modo Ativo      : HIBRIDO_V9")
    print(f"Status do Ciclo : {info_ciclo.get('ciclo', 'N/A')}")
    print(f"Dezenas Faltantes ({qtd_faltantes}): {' '.join(f'{d:02d}' for d in faltantes)}")
    
    if qtd_faltantes <= 5 and qtd_faltantes > 0:
        print("\n" + "!"*45)
        print(f"!!! ALERTA: FECHAMENTO DE CICLO IMINENTE !!!")
        print(f"A IA está priorizando as dezenas: {' '.join(f'{d:02d}' for d in faltantes)}")
        print("!"*45 + "\n")
    elif qtd_faltantes == 0:
         print("\n>>> CICLO FECHADO NO ÚLTIMO CONCURSO. NOVO CICLO INICIADO. <<<\n")
    
    print(f"Índice Volatilidade: {info_ciclo.get('indice_volatilidade', 0.0):.4f}")
    print(f"Peso Recência      : {info_ciclo.get('peso_recencia', 0.0):.2f}\n")

    # Exibição dos Jogos
    print("JOGOS GERADOS COM FILTRO DE CICLO:\n")
    for i, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
        dezenas_formatadas = " ".join(f"{n:02d}" for n in sorted(jogo.dezenas))
        print(f"Jogo {i}: {dezenas_formatadas}")
        print(f"  Score V10             : {score:.6f}")
        print(f"  Repetições (último)   : {repeticoes}")
        print("-" * 40)

    # Conferência
    if hasattr(ultimo_concurso_db, "dezenas") and ultimo_concurso_db.dezenas:
        dezenas_sorteadas = list(ultimo_concurso_db.dezenas)
        print("\n===== CONFERÊNCIA AUTOMÁTICA (ÚLTIMO SORTEIO) =====")
        print(f"Concurso {ultimo_concurso_db.numero} | Resultado: {' '.join(f'{d:02d}' for d in sorted(dezenas_sorteadas))}\n")

        for idx, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
            acertos = contar_acertos(jogo.dezenas, dezenas_sorteadas)
            dezenas_acertadas = sorted(set(jogo.dezenas) & set(dezenas_sorteadas))
            print(f"Jogo {idx}: {acertos} acertos | [{' '.join(f'{d:02d}' for d in dezenas_acertadas)}]")

        salvar_historico_v10(ultimo_concurso_db, dezenas_sorteadas, jogos_motor)
        print("\n[OK] Histórico salvo em 'historico_v10.txt'.")

if __name__ == "__main__":
    main()