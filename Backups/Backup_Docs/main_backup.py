# main.py — Lotofácil Pro V11  |  Entrypoint principal

import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from core.infrastructure.database.database import carregar_concursos
    from core.engine.probabilistic_engine import ProbabilisticEngine
    from core.domain.models import Concurso
except ImportError as exc:
    print(f"\n[ERRO DE ESTRUTURA]: {exc}")
    sys.exit(1)

from typing import Dict, List, Any, Tuple

# ── Constantes da Janela de Ouro ──────────────────────────────────────────
JANELA_OURO_MAX_FALTANTES: int  = 4
JANELA_OURO_MIN_SCORE: float    = 1.18


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS DE APRESENTAÇÃO
# ══════════════════════════════════════════════════════════════════════════

def _linha(char: str = "─", n: int = 65) -> str:
    return char * n


def _status_ciclo(faltantes: List[int], score_medio: float) -> str:
    n = len(faltantes)
    if n == 0:
        return "🔄  INÍCIO DE NOVO CICLO"
    if n <= JANELA_OURO_MAX_FALTANTES and score_medio >= JANELA_OURO_MIN_SCORE:
        return "🏆  JANELA DE OURO ATIVA — MOMENTO IDEAL"
    if n <= JANELA_OURO_MAX_FALTANTES:
        return "🔥  FECHAMENTO DE CICLO PRÓXIMO"
    return "✅  OPORTUNIDADE ESTATÍSTICA ATIVA"


def _exibir_dashboard(
    jogos: List[Tuple[Concurso, float, int]],
    info: Dict[str, Any],
    ultimo: Concurso,
    alvo: int,
    tempo: float,
) -> None:
    faltantes:   List[int] = info.get("dezenas_faltantes", [])
    score_medio: float     = info.get("score_medio", 0.0)
    n_gerados:   int       = info.get("candidatos_gerados", 0)
    n_scored:    int       = info.get("candidatos_scored", 0)
    status: str            = _status_ciclo(faltantes, score_medio)

    print(_linha("═"))
    print("       LOTOFÁCIL PRO V11  —  Motor de Decisão Probabilística")
    print(_linha("═"))
    print(f"  STATUS   : {status}")
    print(_linha("─"))
    print(f"  Concurso : {ultimo.numero} ({ultimo.data})  →  Alvo: #{alvo}")
    falt_str = (
        "  ".join(f"{d:02d}" for d in faltantes)
        if faltantes else "Nenhum — ciclo fechado"
    )
    print(f"  Faltantes: {falt_str}  ({len(faltantes)} de 25)")
    print(f"  Score médio do lote : {score_medio:.6f}")
    print(f"  Tempo de execução   : {tempo:.2f}s  "
          f"({n_gerados} candidatos → {n_scored} pontuados)")
    print(_linha("─"))
    print(f"\n  JOGOS SUGERIDOS PARA O CONCURSO #{alvo}:\n")

    for i, (jogo_obj, score, rep) in enumerate(jogos, 1):
        # Acesso tipado e seguro — jogo_obj é sempre um Concurso
        dezenas: Tuple[int, ...] = jogo_obj.dezenas
        dez_fmt = "  ".join(f"{d:02d}" for d in sorted(dezenas))

        janela_jogo = (
            len(faltantes) <= JANELA_OURO_MAX_FALTANTES
            and score >= JANELA_OURO_MIN_SCORE
        )
        sufixo = "  ★ JANELA DE OURO" if janela_jogo else ""

        print(f"  Jogo {i}: {dez_fmt}{sufixo}")
        print(f"          Score V10: {score:.6f}  |  Repetições: {rep}")
        print()

    print(_linha("═"))


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def main() -> None:
    t0 = time.perf_counter()

    print(_linha("═"))
    print("       LOTOFÁCIL PRO V11 — a iniciar...")
    print(_linha("═"))

    # 1. Carrega concursos (List[Concurso] garantido pela camada de infra)
    concursos: List[Concurso] = carregar_concursos()

    if not concursos:
        print("[AVISO] Base de dados vazia. Importe os dados históricos primeiro.")
        sys.exit(1)

    ultimo: Concurso = concursos[-1]
    alvo: int        = ultimo.numero + 1

    print(f"  ✔  {len(concursos)} concurso(s) carregado(s) — "
          f"último: #{ultimo.numero} ({ultimo.data})\n")

    # 2. Motor — retorno duplo desempacotado e tipado
    engine: ProbabilisticEngine = ProbabilisticEngine()

    jogos: List[Tuple[Concurso, float, int]]
    info:  Dict[str, Any]
    jogos, info = engine.gerar_jogos(concursos)

    t1 = time.perf_counter()

    # 3. Dashboard
    _exibir_dashboard(jogos, info, ultimo, alvo, t1 - t0)

    # 4. Persiste histórico
    engine.salvar_historico_v10(jogos, alvo)
    print("  [OK] Registado em historico_v10.txt\n")


if __name__ == "__main__":
    main()
