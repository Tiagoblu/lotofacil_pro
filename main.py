import requests
import sqlite3
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
    """Retorna a quantidade de dezenas que o jogo acertou."""
    return len(set(jogo_dezenas) & set(dezenas_sorteadas))


def salvar_historico_v10(
    ultimo_concurso_db,
    dezenas_sorteadas,
    jogos_motor,
    caminho_arquivo: str = "historico_v10.txt",
):
    """
    Salva em texto:
    - data/hora da execução
    - número do concurso conferido
    - resultado do concurso
    - cada jogo gerado (dezenas, score, repetições)
    - acertos e dezenas acertadas
    """
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
    print("==== LotoFácil Pro V10 – Motor Estrutural Adaptativo ====\n")

    print("Inicializando banco...")
    inicializar_banco()
    print("Banco pronto.\n")

    print("Verificando novos concursos na API...")
    novos, ultimo_concurso_numero = baixar_e_salvar_novos_concursos()
    if novos > 0:
        print(f"{novos} novo(s) concurso(s) baixado(s). Último: {ultimo_concurso_numero}\n")
    else:
        print(f"Banco já atualizado. Último concurso: {ultimo_concurso_numero}\n")

    concursos = ConcursoRepository.obter_todos()
    print(f"Total de concursos: {len(concursos)}\n")

    # ------------------------------------------------------------------
    # Geração dos jogos pelo Motor Probabilístico (V10)
    # ------------------------------------------------------------------
    if not concursos:
        print("Nenhum concurso encontrado no banco para gerar jogos.")
        return

    ultimo_concurso_db = concursos[-1]
    print(f"Último concurso no banco: {ultimo_concurso_db.numero}")
    print(f"Gerando jogos para o próximo: {ultimo_concurso_db.numero + 1}\n")

    print("Gerando candidatos com Motor Probabilístico...\n")
    modo_estrategia = "BALANCEADO"

    jogos_motor, info_ciclo = ProbabilisticEngine.gerar_jogos(
        concursos,
        quantidade=5,
        candidatos=300,
        modo=modo_estrategia,
    )

    print(f"Modo Estratégico Ativo : {modo_estrategia}")
    print(f"Ciclo Detectado (V10)  : {info_ciclo['ciclo']}")
    print(f"Índice de Volatilidade : {info_ciclo['indice_volatilidade']:.4f}")
    print(f"Peso Recência          : {info_ciclo['peso_recencia']:.2f}\n")
    print("Jogos Finais:\n")

    for i, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
        dezenas_formatadas = " ".join(f"{n:02d}" for n in jogo.dezenas)
        print(f"Jogo {i}: {dezenas_formatadas}")
        print(f"Score V10             : {score:.6f}")
        print(f"Repetições Anteriores : {repeticoes}")
        print("-" * 60)

    # ------------------------------------------------------------------
    # Conferência automática com o último concurso já sorteado
    # ------------------------------------------------------------------
    if hasattr(ultimo_concurso_db, "dezenas") and ultimo_concurso_db.dezenas:
        dezenas_sorteadas = list(ultimo_concurso_db.dezenas)

        print("\n===== CONFERÊNCIA COM O ÚLTIMO CONCURSO SORTEADO =====")
        print(
            f"Concurso {ultimo_concurso_db.numero} | Resultado: "
            + " ".join(f"{d:02d}" for d in sorted(dezenas_sorteadas))
        )
        print()

        for idx, (jogo, score, repeticoes) in enumerate(jogos_motor, start=1):
            dezenas_jogo = sorted(jogo.dezenas)
            acertos = contar_acertos(dezenas_jogo, dezenas_sorteadas)
            dezenas_acertadas = sorted(set(dezenas_jogo) & set(dezenas_sorteadas))

            print(f"Jogo {idx}: {' '.join(f'{d:02d}' for d in dezenas_jogo)}")
            print(f"  Acertos: {acertos}")
            print(
                f"  Dezenas acertadas: {' '.join(f'{d:02d}' for d in dezenas_acertadas)}\n"
            )

        # Salva tudo no arquivo de histórico
        salvar_historico_v10(
            ultimo_concurso_db=ultimo_concurso_db,
            dezenas_sorteadas=dezenas_sorteadas,
            jogos_motor=jogos_motor,
            caminho_arquivo="historico_v10.txt",
        )
        print("Histórico desta execução salvo em 'historico_v10.txt'.")
    else:
        print(
            "\nNão foi possível conferir os jogos: o último concurso no banco não tem dezenas sorteadas ou não existe."
        )


if __name__ == "__main__":
    main()