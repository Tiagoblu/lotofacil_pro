# core/engine/probabilistic_engine.py
#
# Motor Probabilístico V11 — Arquitectura Elite de 3 Fases
# ─────────────────────────────────────────────────────────
#  FASE 1 — Pré-cálculo estatístico (feito UMA vez, O(n))
#  FASE 2 — Geração inteligente de candidatos (ZERO chamadas a score_v10)
#  FASE 3 — Pontuação selectiva (apenas ~120 candidatos → pré-filtrados)
#
# Bugs corrigidos vs. versão anterior:
#  ✔ Truncamento [:15]  → construção garantida de exactamente 15 dezenas
#  ✔ Vagas negativas    → construção correcta sem union descontrolada
#  ✔ 100 k chamadas     → máximo de CANDIDATOS_PARA_SCORE chamadas a score_v10
#  ✔ Todos os faltantes → inclusão SOFT (0-3), não forçada

import random
import datetime
from collections import Counter
from typing import Any, Dict, FrozenSet, List, Set, Tuple

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10


class ProbabilisticEngine:
    """Motor Probabilístico V11 — High-Speed Elite Search."""

    # ── Hiperparâmetros (ajuste aqui se necessário) ────────────────────────
    JANELA_FREQUENCIA: int      = 30    # concursos recentes para pesos de freq.
    REP_MIN: int                = 8     # mín. dezenas repetidas do último concurso
    REP_MAX: int                = 11    # máx. dezenas repetidas do último concurso
    CANDIDATOS_POOL: int        = 2000  # candidatos gerados na Fase 2 (sem score)
    CANDIDATOS_PARA_SCORE: int  = 150   # candidatos que avançam para score_v10
    SCORE_MIN_ELITE: float      = 1.18  # limiar da Janela de Ouro
    # ───────────────────────────────────────────────────────────────────────

    # ══════════════════════════════════════════════════════════════════════
    #  UTILITÁRIOS PÚBLICOS
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def identificar_dezenas_faltantes(concursos: List[Concurso]) -> List[int]:
        """
        Dezenas de 1-25 que ainda não apareceram no ciclo actual.
        Um ciclo fecha quando todos os 25 números tiverem saído pelo menos uma vez.
        """
        todas: Set[int] = set(range(1, 26))
        vistas: Set[int] = set()
        for c in concursos:
            vistas.update(c.dezenas)
            if len(vistas) == 25:
                vistas = set()          # inicia novo ciclo
        return sorted(todas - vistas)

    # ══════════════════════════════════════════════════════════════════════
    #  FASE 1 — PRÉ-CÁLCULO ESTATÍSTICO
    # ══════════════════════════════════════════════════════════════════════

    def _calcular_pesos_frequencia(
        self,
        concursos: List[Concurso],
    ) -> Dict[int, float]:
        """
        Frequência relativa de cada dezena nos últimos JANELA_FREQUENCIA concursos.
        Laplace smoothing leve (0.01) para dezenas com zero ocorrências recentes.
        """
        recentes = concursos[-self.JANELA_FREQUENCIA :]
        counter: Counter = Counter()
        for c in recentes:
            counter.update(c.dezenas)
        total: int = sum(counter.values()) or 1
        return {d: max(counter.get(d, 0) / total, 0.01) for d in range(1, 26)}

    # ══════════════════════════════════════════════════════════════════════
    #  FASE 2 — GERAÇÃO INTELIGENTE DE CANDIDATOS
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _amostrar_ponderado(
        pool: List[int],
        pesos: List[float],
        k: int,
    ) -> List[int]:
        """
        Amostragem ponderada SEM reposição para pools de ≤ 25 elementos.
        Garante exactamente k elementos distintos.
        """
        pool_copia  = pool[:]
        pesos_copia = pesos[:]
        selecionados: List[int] = []

        for _ in range(min(k, len(pool_copia))):
            total = sum(pesos_copia)
            if total <= 0:
                idx = random.randrange(len(pool_copia))
            else:
                r, acum = random.uniform(0, total), 0.0
                idx = len(pool_copia) - 1          # fallback seguro
                for i, p in enumerate(pesos_copia):
                    acum += p
                    if acum >= r:
                        idx = i
                        break
            selecionados.append(pool_copia[idx])
            pool_copia.pop(idx)
            pesos_copia.pop(idx)

        return selecionados

    def _gerar_candidato(
        self,
        dezenas_ultimo_lista: List[int],
        faltantes_lista: List[int],
        faltantes_set: Set[int],
        complemento_lista: List[int],       # números fora de dezenas_ultimo E fora de faltantes
        pesos: Dict[int, float],
    ) -> Tuple[int, ...]:
        """
        Gera um jogo de EXACTAMENTE 15 dezenas sem qualquer truncamento.

        Construção em 3 camadas:
          1. Base   — n_rep dezenas do último concurso  (REP_MIN a REP_MAX)
          2. Soft   — 0-3 faltantes do ciclo actual     (preferência, não obrigação)
          3. Fill   — restante por amostragem ponderada por frequência
        """
        # ── Camada 1: Base (repetições do último concurso) ─────────────────
        n_rep = random.randint(self.REP_MIN, self.REP_MAX)
        n_rep = min(n_rep, len(dezenas_ultimo_lista))
        base: Set[int] = set(random.sample(dezenas_ultimo_lista, n_rep))
        vagas = 15 - n_rep                          # sempre > 0 (REP_MAX ≤ 11 < 15)

        # ── Camada 2: Faltantes (soft) ─────────────────────────────────────
        # Quando o ciclo reinicia faltantes_set == {1..25}, incluindo números
        # já em `base`. Filtramos `base` aqui para garantir zero sobreposição
        # entre as camadas 1 e 2.
        disponiveis_falt = [f for f in faltantes_lista if f not in base]
        max_falt = min(3, vagas, len(disponiveis_falt))
        n_falt   = random.randint(0, max_falt)
        falt_escolhidos = random.sample(disponiveis_falt, n_falt) if n_falt else []
        vagas -= n_falt

        # ── Camada 3: Complemento ponderado por frequência ────────────────
        # `ocupados` = tudo o que já está reservado nas camadas 1 e 2.
        # O pool_fill NUNCA pode conter elementos de `ocupados`, caso contrário
        # a union final produz < 15 dezenas quando o ciclo acabou de reiniciar
        # (situação em que faltantes_set == {1..25} e inclui dezenas da base).
        ocupados: Set[int] = base | set(falt_escolhidos)

        pool_comp  = [n for n in complemento_lista if n not in faltantes_set and n not in ocupados]
        # Faltantes ainda disponíveis (não escolhidos na camada 2 e não em base)
        pool_extra = [f for f in faltantes_lista if f not in ocupados]

        pool_fill  = pool_comp + pool_extra
        pesos_fill = [pesos[n] for n in pool_fill]

        fill = self._amostrar_ponderado(pool_fill, pesos_fill, vagas)

        dezenas = tuple(sorted(base | set(falt_escolhidos) | set(fill)))

        # Salvaguarda de integridade — nunca deve falhar com construção correcta
        assert len(dezenas) == 15, (
            f"[BUG] Candidato com {len(dezenas)} dezenas gerado. "
            f"base={len(base)}, falt={len(falt_escolhidos)}, fill={len(fill)}"
        )
        return dezenas

    # ══════════════════════════════════════════════════════════════════════
    #  PRÉ-SCORE LEVE (sem score_v10) — Fase 2 → Fase 3
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _prescore(
        dezenas: Tuple[int, ...],
        dezenas_ultimo_set: Set[int],
        faltantes_set: Set[int],
        pesos: Dict[int, float],
    ) -> float:
        """
        Pontuação leve para ordenar candidatos antes de chamar score_v10.
        Captura os principais factores estatísticos da Lotofácil:
          - Frequência recente das dezenas
          - Sobreposição com o último concurso (9-10 é o óptimo histórico)
          - Paridade (7-8 pares é o patamar mais frequente)
          - Soma típica do sorteio (170-215)
          - Inclusão de faltantes do ciclo
        """
        s = set(dezenas)

        # Frequência recente (principal preditor)
        freq = sum(pesos.get(d, 0.01) for d in dezenas)

        # Repetições com último concurso
        rep = len(s & dezenas_ultimo_set)
        rep_mult = {8: 0.88, 9: 1.00, 10: 1.00, 11: 0.92}.get(rep, 0.55)

        # Paridade
        pares = sum(1 for d in dezenas if d % 2 == 0)
        par_mult = 1.0 if 6 <= pares <= 9 else 0.70

        # Soma típica
        soma = sum(dezenas)
        soma_mult = 1.0 if 165 <= soma <= 220 else 0.65

        # Bónus de faltantes (suave)
        falt_bonus = len(s & faltantes_set) * 0.04

        return freq * rep_mult * par_mult * soma_mult + falt_bonus

    # ══════════════════════════════════════════════════════════════════════
    #  FASE 3 — EXTRACÇÃO DO SCORE v10
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _extrair_score(resultado: Any) -> float:
        """
        Extrai o valor numérico do retorno de calcular_score_v10,
        independentemente do tipo (objecto com atributo ou valor directo).
        """
        if hasattr(resultado, "score_final"):
            return float(resultado.score_final)
        if hasattr(resultado, "score"):
            return float(resultado.score)
        return float(resultado)

    # ══════════════════════════════════════════════════════════════════════
    #  API PÚBLICA
    # ══════════════════════════════════════════════════════════════════════

    def gerar_jogos(
        self,
        concursos: List[Concurso],
        quantidade: int = 5,
    ) -> Tuple[List[Tuple[Concurso, float, int]], Dict[str, Any]]:
        """
        Gera `quantidade` jogos de elite com score máximo e latência mínima.

        Fluxo:
          1. Pré-cálculo estatístico  — O(n), feito uma única vez
          2. Geração de candidatos    — CANDIDATOS_POOL iterações, ZERO score_v10
          3. Pré-ordenação por prescore leve
          4. score_v10 nos top CANDIDATOS_PARA_SCORE
          5. Devolve top `quantidade` por score_v10

        Returns:
            Tuple[
                List[Tuple[Concurso, float, int]],  # (jogo, score, repetições)
                Dict[str, Any]                       # ciclo_info
            ]
        """
        if not concursos:
            raise ValueError("A lista de concursos não pode estar vazia.")

        # ── PRÉ-CÁLCULO (uma vez) ─────────────────────────────────────────
        ultimo: Concurso               = concursos[-1]
        dezenas_ultimo_set:   Set[int] = set(ultimo.dezenas)
        dezenas_ultimo_lista: List[int] = list(ultimo.dezenas)

        faltantes_raw: List[int]       = self.identificar_dezenas_faltantes(concursos)

        # Quando todos os 25 números são "faltantes", o ciclo acabou de
        # reiniciar. Neste estado a camada de faltantes não tem poder
        # discriminante (todos os números são iguais). Zeramos para que
        # o motor opere em modo frequência pura → scores mais altos.
        novo_ciclo: bool           = (len(faltantes_raw) == 25)
        faltantes_lista: List[int] = [] if novo_ciclo else faltantes_raw
        faltantes_set:  Set[int]   = set(faltantes_lista)

        pesos: Dict[int, float]    = self._calcular_pesos_frequencia(concursos)

        # Complemento = números que NÃO estão no último concurso e NÃO são faltantes
        complemento_lista: List[int] = [
            n for n in range(1, 26)
            if n not in dezenas_ultimo_set and n not in faltantes_set
        ]

        # ── FASE 2 — Geração de candidatos (ZERO score_v10) ───────────────
        candidatos: List[Tuple[int, ...]] = []
        vistos: Set[FrozenSet[int]]       = set()
        tentativas_max: int               = self.CANDIDATOS_POOL * 5

        for _ in range(tentativas_max):
            if len(candidatos) >= self.CANDIDATOS_POOL:
                break
            dez = self._gerar_candidato(
                dezenas_ultimo_lista,
                faltantes_lista,
                faltantes_set,
                complemento_lista,
                pesos,
            )
            fs: FrozenSet[int] = frozenset(dez)
            if fs not in vistos:
                vistos.add(fs)
                candidatos.append(dez)

        # ── Pré-ordenação por prescore leve ───────────────────────────────
        candidatos.sort(
            key=lambda d: self._prescore(d, dezenas_ultimo_set, faltantes_set, pesos),
            reverse=True,
        )

        # ── FASE 3 — score_v10 apenas nos top N candidatos ────────────────
        top: List[Tuple[int, ...]] = candidatos[: self.CANDIDATOS_PARA_SCORE]

        jogos_scored: List[Tuple[Concurso, float, int]] = []
        for dez in top:
            jogo_obj  = Concurso(numero=0, data="", dezenas=dez)
            resultado = calcular_score_v10(jogo_obj, concursos)
            score     = self._extrair_score(resultado)
            rep       = len(set(dez) & dezenas_ultimo_set)
            jogos_scored.append((jogo_obj, score, rep))

        jogos_scored.sort(key=lambda x: x[1], reverse=True)
        jogos_finais = jogos_scored[:quantidade]

        # ── Ciclo info ────────────────────────────────────────────────────
        score_medio: float = (
            sum(j[1] for j in jogos_finais) / len(jogos_finais)
            if jogos_finais else 0.0
        )

        ciclo_info: Dict[str, Any] = {
            "dezenas_faltantes":  faltantes_raw,   # sempre os reais, para exibição
            "novo_ciclo":         novo_ciclo,
            "total_concursos":    len(concursos),
            "score_medio":        score_medio,
            "candidatos_gerados": len(candidatos),
            "candidatos_scored":  len(top),
        }

        return jogos_finais, ciclo_info

    # ══════════════════════════════════════════════════════════════════════
    #  PERSISTÊNCIA
    # ══════════════════════════════════════════════════════════════════════

    def salvar_historico_v10(
        self,
        jogos: List[Tuple[Concurso, float, int]],
        alvo: int,
    ) -> None:
        """Persiste os jogos gerados em historico_v10.txt (append)."""
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open("historico_v10.txt", "a", encoding="utf-8") as f:
                f.write("-" * 80 + "\n")
                f.write(f"Execução em: {timestamp}\n")
                f.write(f"Sugestões para o Concurso Alvo: {alvo}\n\n")
                for i, (jogo_obj, score, rep) in enumerate(jogos, 1):
                    dez_str = " ".join(f"{d:02d}" for d in sorted(jogo_obj.dezenas))
                    f.write(f"Jogo {i}: {dez_str}\n")
                    f.write(f"  Score V10             : {score:.6f}\n")
                    f.write(f"  Repetições Anteriores : {rep}\n\n")
        except Exception as exc:
            print(f"[ERRO HISTÓRICO]: {exc}")
