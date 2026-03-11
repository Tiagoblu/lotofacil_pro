"""
analisar_motor_v10.py
Analisa o perfil estatístico dos jogos gerados pelo Motor V10
e compara com o DNA alvo do Motor V9.

Uso:
    py analisar_motor_v10.py
    py analisar_motor_v10.py --modo AGRESSIVO --jogos 5000
"""

import sys
import os
import csv
import argparse
import datetime
import statistics
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ── Imports do projeto (nomes reais confirmados) ──────────────────────────────
try:
    from core.infrastructure.database.database   import inicializar_banco
    from core.infrastructure.database.repository import ConcursoRepository
    from core.engine.probabilistic_engine        import ProbabilisticEngine
except ImportError as e:
    print(f"\nErro ao importar modulos do projeto:\n   {e}")
    print("Verifique se esta rodando a partir da raiz do projeto.\n")
    sys.exit(1)


# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═════════════════════════════════════════════════════════════════════════════

TOTAL_JOGOS_PADRAO = 2_000
MODO_PADRAO        = "BALANCEADO"
CSV_SAIDA          = os.path.join(ROOT, "data", "cache", "perfil_v10.csv")

# DNA alvo medido do V9 (fonte: analisar_motor_v9.py, 2000 jogos)
DNA_V9 = {
    "soma_media"      : 221.77,
    "soma_min_ideal"  : 171,
    "soma_max_ideal"  : 262,
    "pares_media"     : 7.21,
    "impares_media"   : 7.79,
    "faixas_medias"   : [1.92, 2.52, 3.02, 3.55, 3.98],
    "repeticao_media" : 7.14,
    "repeticao_alvo"  : "7-8",
}

TOLERANCIA = {
    "soma"      : 3.0,
    "pares"     : 0.5,
    "repeticao" : 0.5,
    "faixa"     : 0.20,
}

NOMES_FAIXAS = ["1-5 ", "6-10", "11-15", "16-20", "21-25"]
SEP          = "=" * 66
SEP2         = "-" * 66


# ═════════════════════════════════════════════════════════════════════════════
# MÉTRICAS POR JOGO
# ═════════════════════════════════════════════════════════════════════════════

def calcular_soma(jogo):
    return sum(jogo)

def calcular_pares(jogo):
    return sum(1 for d in jogo if d % 2 == 0)

def calcular_faixas(jogo):
    limites = [(1,5),(6,10),(11,15),(16,20),(21,25)]
    return [sum(1 for d in jogo if a <= d <= b) for a, b in limites]

def calcular_repeticao(jogo, ultimo):
    return len(set(jogo) & set(ultimo))

def calcular_maior_sequencia(jogo):
    s = sorted(jogo)
    max_seq = seq = 1
    for i in range(1, len(s)):
        seq = seq + 1 if s[i] == s[i-1] + 1 else 1
        max_seq = max(max_seq, seq)
    return max_seq


# ═════════════════════════════════════════════════════════════════════════════
# ESTATÍSTICAS AGREGADAS
# ═════════════════════════════════════════════════════════════════════════════

def media(lst):
    return round(statistics.mean(lst), 3)

def desvio(lst):
    return round(statistics.stdev(lst), 3) if len(lst) > 1 else 0.0

def dist_pct(lst):
    total = len(lst)
    return {k: round(v/total*100, 1) for k, v in sorted(Counter(lst).items())}

def barra(valor, maximo, largura=20):
    p = min(int(round(valor / maximo * largura)), largura)
    return "#" * p + "." * (largura - p)

def delta_str(real, alvo, tol):
    diff  = real - alvo
    icone = "OK" if abs(diff) <= tol else ("ALTO" if diff > 0 else "BAIXO")
    return f"{diff:+.3f}  [{icone}]"


# ═════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS
# ═════════════════════════════════════════════════════════════════════════════

def carregar_dados():
    inicializar_banco()
    todos  = ConcursoRepository.obter_todos()
    ultimo = ConcursoRepository.obter_ultimo()
    if not todos or not ultimo:
        print("Nenhum concurso encontrado no banco.")
        sys.exit(1)
    ultimo_dezenas = sorted(ultimo.dezenas)
    print(f"   Concursos carregados : {len(todos):,}")
    print(f"   Ultimo concurso      : {ultimo_dezenas}")
    return todos, ultimo_dezenas


# ═════════════════════════════════════════════════════════════════════════════
# GERAÇÃO DE JOGOS
# ═════════════════════════════════════════════════════════════════════════════

def gerar_jogos(total, todos_concursos, modo):
    """
    Gera jogos usando ProbabilisticEngine.gerar_jogos() — método real confirmado.
    Distribui a geração pelos últimos 200 concursos,
    mesmo critério do backtest e do analisar_motor_v9.py.

    Estratégia:
        - Divide os 200 concursos em blocos.
        - Em cada bloco gera um lote de candidatos com historico progressivo.
        - Coleta os melhores jogos de cada lote até atingir o total desejado.
    """
    concursos_analise = todos_concursos[-200:]
    n_total           = len(todos_concursos)
    jogos_por_conc    = max(1, total // len(concursos_analise))
    # candidatos por chamada: quanto mais candidatos, mais seletivo o engine
    candidatos_por_chamada = jogos_por_conc * 10

    jogos = []

    for i, _ in enumerate(concursos_analise):
        historico = todos_concursos[:n_total - (len(concursos_analise) - i)]
        if len(historico) < 10:
            continue

        try:
            resultado, _ = ProbabilisticEngine.gerar_jogos(
                concursos  = historico,
                quantidade = jogos_por_conc,
                candidatos = candidatos_por_chamada,
                modo       = modo,
            )
        except Exception as e:
            print(f"\n   Aviso: erro ao gerar lote [{i}]: {e}")
            continue

        # resultado é lista de (Concurso, score, repeticoes)
        for jogo_obj, _score, _rep in resultado:
            jogos.append(sorted(jogo_obj.dezenas))

        feitos = min(len(jogos), total)
        pct    = feitos / total * 100
        print(f"\r   Gerando... {feitos:,}/{total:,} ({pct:.0f}%)",
              end="", flush=True)

        if len(jogos) >= total:
            break

    print()
    return jogos[:total]


# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISE
# ═════════════════════════════════════════════════════════════════════════════

def analisar(jogos, ultimo_concurso):
    somas    = [calcular_soma(j)                       for j in jogos]
    pares_l  = [calcular_pares(j)                      for j in jogos]
    faixas_l = [calcular_faixas(j)                     for j in jogos]
    reps_l   = [calcular_repeticao(j, ultimo_concurso) for j in jogos]
    seqs_l   = [calcular_maior_sequencia(j)            for j in jogos]

    faixas_medias = [media([f[i] for f in faixas_l]) for i in range(5)]

    return {
        "soma"      : {"media": media(somas),   "desvio": desvio(somas),
                       "min"  : min(somas),     "max"   : max(somas)},
        "pares"     : {"media": media(pares_l), "desvio": desvio(pares_l)},
        "impares"   : {"media": round(15 - media(pares_l), 3)},
        "faixas"    : faixas_medias,
        "repeticao" : {"media": media(reps_l),  "desvio": desvio(reps_l),
                       "dist" : dist_pct(reps_l)},
        "sequencia" : {"media": media(seqs_l),  "desvio": desvio(seqs_l),
                       "max"  : max(seqs_l),    "dist"  : dist_pct(seqs_l)},
    }


# ═════════════════════════════════════════════════════════════════════════════
# DIAGNÓSTICO AUTOMÁTICO
# ═════════════════════════════════════════════════════════════════════════════

def diagnosticar(resultado):
    problemas = []

    # Soma
    diff = resultado["soma"]["media"] - DNA_V9["soma_media"]
    if abs(diff) > TOLERANCIA["soma"]:
        acao = "Aumentar" if diff < 0 else "Reduzir"
        problemas.append({
            "secao"    : "Soma",
            "descricao": f"Soma media {resultado['soma']['media']:.2f} "
                         f"vs alvo {DNA_V9['soma_media']:.2f} (delta {diff:+.2f})",
            "acao"     : f"{acao} PESO_SOMA em score_v10.py",
        })

    # Pares
    diff = resultado["pares"]["media"] - DNA_V9["pares_media"]
    if abs(diff) > TOLERANCIA["pares"]:
        excesso = "pares" if diff > 0 else "impares"
        problemas.append({
            "secao"    : "Pares/Impares",
            "descricao": f"Excesso de {excesso} (delta {diff:+.2f})",
            "acao"     : "Verificar filtro de equilibrio par/impar no V10",
        })

    # Repeticao
    diff = resultado["repeticao"]["media"] - DNA_V9["repeticao_media"]
    if abs(diff) > TOLERANCIA["repeticao"]:
        acao = "Aumentar" if diff < 0 else "Reduzir"
        problemas.append({
            "secao"    : "Repeticao",
            "descricao": f"Repeticao media {resultado['repeticao']['media']:.2f} "
                         f"vs alvo {DNA_V9['repeticao_media']:.2f} (delta {diff:+.2f})",
            "acao"     : f"{acao} max_repeticoes no ProbabilisticEngine ou "
                         f"ajustar penalizacao de repeticao em score_v10.py",
        })

    # Faixas
    for i, nome in enumerate(NOMES_FAIXAS):
        diff = resultado["faixas"][i] - DNA_V9["faixas_medias"][i]
        if abs(diff) > TOLERANCIA["faixa"]:
            acao = "Aumentar" if diff < 0 else "Reduzir"
            problemas.append({
                "secao"    : f"Faixa {nome}",
                "descricao": f"Faixa {nome}: {resultado['faixas'][i]:.3f} "
                             f"vs alvo {DNA_V9['faixas_medias'][i]:.2f} "
                             f"(delta {diff:+.3f})",
                "acao"     : f"{acao} peso da faixa {nome} em score_v10.py",
            })

    return problemas


# ═════════════════════════════════════════════════════════════════════════════
# RELATÓRIO NO TERMINAL
# ═════════════════════════════════════════════════════════════════════════════

def imprimir_relatorio(resultado, problemas, total_jogos, modo, total_conc, ultimo):
    print()
    print(SEP)
    print("  LotoFacil Pro - Analise de Perfil  Motor V10")
    print(f"  Jogos analisados : {total_jogos:,}   |   Modo : {modo}")
    print(f"  Concursos no BD  : {total_conc:,}")
    print(f"  Ultimo concurso  : {ultimo}")
    print(SEP)

    # 1. Soma
    s = resultado["soma"]
    print("\n1. SOMA DAS DEZENAS")
    print(SEP2)
    print(f"  Media   V10 : {s['media']:.3f}")
    print(f"  Alvo    V9  : {DNA_V9['soma_media']:.2f}   "
          f"{delta_str(s['media'], DNA_V9['soma_media'], TOLERANCIA['soma'])}")
    print(f"  Desvio      : {s['desvio']:.3f}")
    print(f"  Minima      : {s['min']}   (ideal >= {DNA_V9['soma_min_ideal']})")
    print(f"  Maxima      : {s['max']}   (ideal <= {DNA_V9['soma_max_ideal']})")

    # 2. Pares / Ímpares
    p  = resultado["pares"]
    ii = resultado["impares"]
    print("\n2. PARES / IMPARES")
    print(SEP2)
    print(f"  Pares    V10 : {p['media']:.3f}   "
          f"Alvo V9 : {DNA_V9['pares_media']:.2f}   "
          f"{delta_str(p['media'], DNA_V9['pares_media'], TOLERANCIA['pares'])}")
    print(f"  Impares  V10 : {ii['media']:.3f}   "
          f"Alvo V9 : {DNA_V9['impares_media']:.2f}   "
          f"{delta_str(ii['media'], DNA_V9['impares_media'], TOLERANCIA['pares'])}")

    # 3. Faixas
    print("\n3. DISTRIBUICAO POR FAIXAS")
    print(SEP2)
    print(f"  {'Faixa':<8} {'V10':>7}  {'V9 alvo':>9}  {'Delta':>14}  Barra V10")
    print(f"  {'-'*8} {'-'*7}  {'-'*9}  {'-'*14}  {'-'*22}")
    for idx, nome in enumerate(NOMES_FAIXAS):
        v10_val = resultado["faixas"][idx]
        v9_val  = DNA_V9["faixas_medias"][idx]
        print(f"  {nome:<8} {v10_val:>7.3f}  {v9_val:>9.2f}  "
              f"{delta_str(v10_val, v9_val, TOLERANCIA['faixa']):>14}  "
              f"{barra(v10_val, 5.0)}")

    # 4. Repetição
    r = resultado["repeticao"]
    print("\n4. REPETICAO COM ULTIMO CONCURSO")
    print(SEP2)
    print(f"  Media   V10 : {r['media']:.3f}   "
          f"Alvo V9 : {DNA_V9['repeticao_media']:.2f}   "
          f"{delta_str(r['media'], DNA_V9['repeticao_media'], TOLERANCIA['repeticao'])}")
    print(f"  Desvio      : {r['desvio']:.3f}   "
          f"(faixa ideal: {DNA_V9['repeticao_alvo']} dezenas)")
    print(f"\n  Distribuicao percentual:")
    for qtd, pct in r["dist"].items():
        marcador = "  <- alvo" if qtd in (7, 8) else ""
        print(f"    {qtd:>4} rep  {pct:>5.1f}%  "
              f"{barra(pct, 25.0, 18)}{marcador}")

    # 5. Sequências
    sq = resultado["sequencia"]
    print("\n5. SEQUENCIAS CONSECUTIVAS")
    print(SEP2)
    print(f"  Media maior seq. : {sq['media']:.3f}")
    print(f"  Maximo observado : {sq['max']}")
    print(f"  Desvio           : {sq['desvio']:.3f}")
    print(f"\n  Distribuicao (tamanho da maior sequencia):")
    for tam, pct in sq["dist"].items():
        alerta = "  [PENALIZAR]" if tam >= 6 else ""
        print(f"    seq {tam}  {pct:>5.1f}%  "
              f"{barra(pct, 40.0, 15)}{alerta}")

    # Diagnóstico final
    print()
    print(SEP)
    print("  DIAGNOSTICO  -  V10 vs DNA alvo (V9)")
    print(SEP)

    if not problemas:
        print("  [OK] Perfil do V10 esta ALINHADO com o DNA do V9!")
        print()
        print("  Proximos passos:")
        print("    1. Rodar backtest com 500 concursos")
        print("    2. Confirmar Media >= 9.10 e %11+ >= 12.5%")
        print("    3. Se KPIs atingidos -> Fase 1 concluida")
    else:
        print(f"  {len(problemas)} divergencia(s) encontrada(s):\n")
        for i, pb in enumerate(problemas, 1):
            print(f"  [{i}] Secao   : {pb['secao']}")
            print(f"      Problema: {pb['descricao']}")
            print(f"      Acao    : {pb['acao']}")
            print()
        print("  Fluxo recomendado:")
        print("     1. Ajustar score_v10.py conforme as acoes acima")
        print("     2. Rodar este script novamente")
        print("     3. Repetir ate [OK] em todos os itens")
        print("     4. Rodar backtest 500 concursos para confirmar KPIs")

    print(SEP)
    print()


# ═════════════════════════════════════════════════════════════════════════════
# EXPORTAR CSV
# ═════════════════════════════════════════════════════════════════════════════

def exportar_csv(resultado, problemas, total_jogos, modo):
    os.makedirs(os.path.dirname(CSV_SAIDA), exist_ok=True)
    agora  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    campos = [
        "timestamp", "modo", "total_jogos",
        "soma_media", "soma_desvio", "soma_min", "soma_max",
        "pares_media", "impares_media",
        "faixa_1_5", "faixa_6_10", "faixa_11_15", "faixa_16_20", "faixa_21_25",
        "repeticao_media", "repeticao_desvio",
        "sequencia_media", "sequencia_max",
        "n_problemas",
    ]
    valores = [
        agora, modo, total_jogos,
        resultado["soma"]["media"],      resultado["soma"]["desvio"],
        resultado["soma"]["min"],        resultado["soma"]["max"],
        resultado["pares"]["media"],     resultado["impares"]["media"],
        resultado["faixas"][0],          resultado["faixas"][1],
        resultado["faixas"][2],          resultado["faixas"][3],
        resultado["faixas"][4],
        resultado["repeticao"]["media"], resultado["repeticao"]["desvio"],
        resultado["sequencia"]["media"], resultado["sequencia"]["max"],
        len(problemas),
    ]
    escrever_cab = not os.path.exists(CSV_SAIDA)
    with open(CSV_SAIDA, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if escrever_cab:
            w.writerow(campos)
        w.writerow(valores)
    print(f"  Metricas salvas em -> {CSV_SAIDA}")


# ═════════════════════════════════════════════════════════════════════════════
# ARGPARSE
# ═════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="LotoFacil Pro - Analise de Perfil do Motor V10"
    )
    parser.add_argument(
        "--modo",
        choices=["CONSERVADOR", "BALANCEADO", "AGRESSIVO"],
        default=MODO_PADRAO,
    )
    parser.add_argument(
        "--jogos",
        type=int,
        default=TOTAL_JOGOS_PADRAO,
    )
    parser.add_argument(
        "--sem-csv",
        action="store_true",
    )
    return parser.parse_args()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    args        = parse_args()
    modo        = args.modo
    total_jogos = args.jogos

    print()
    print("Carregando concursos do banco de dados...")
    todos, ultimo = carregar_dados()

    print(f"\nGerando {total_jogos:,} jogos  |  Motor V10  |  Modo: {modo}")
    jogos = gerar_jogos(total_jogos, todos, modo)

    if not jogos:
        print("Nenhum jogo foi gerado. Verifique a implementacao do engine.")
        sys.exit(1)

    print(f"Calculando metricas sobre {len(jogos):,} jogos...")
    resultado = analisar(jogos, ultimo)
    problemas = diagnosticar(resultado)

    imprimir_relatorio(resultado, problemas, len(jogos), modo, len(todos), ultimo)

    if not args.sem_csv:
        exportar_csv(resultado, problemas, len(jogos), modo)


if __name__ == "__main__":
    main()