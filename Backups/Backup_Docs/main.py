# main.py — Lotofácil Pro V11  |  Entrypoint principal
#
# Fluxo:
#  1. Sincroniza banco local com API da Caixa  (baixar.py)
#  2. Carrega concursos                         (database.py → List[Concurso])
#  3. Gera jogos de elite                       (probabilistic_engine.py)
#  4. Exibe dashboard Rich com Janela de Ouro
#  5. Persiste histórico em historico_v10.txt

import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import print as rprint
except ImportError:
    print("[ERRO] Biblioteca 'rich' não instalada. Execute: pip install rich")
    sys.exit(1)

try:
    from core.infrastructure.database.database import carregar_concursos
    from core.infrastructure.downloader.baixar import baixar_dados_novos
    from core.engine.probabilistic_engine import ProbabilisticEngine
    from core.domain.models import Concurso
except ImportError as exc:
    print(f"\n[ERRO DE ESTRUTURA]: {exc}")
    sys.exit(1)

from typing import Dict, List, Any, Tuple

# ── Constantes da Janela de Ouro ──────────────────────────────────────────
JANELA_OURO_MAX_FALTANTES: int  = 4
JANELA_OURO_MIN_SCORE:     float = 1.18

console = Console()


# ══════════════════════════════════════════════════════════════════════════
#  APRESENTAÇÃO
# ══════════════════════════════════════════════════════════════════════════

def exibir_cabecalho() -> None:
    console.print(Panel.fit(
        "[bold cyan]LOTOFÁCIL PRO V11[/bold cyan] — "
        "[italic white]Sistema de Análise Preditiva[/italic white]",
        border_style="bright_blue",
        subtitle="[bold blue]V11.2 - High Performance[/bold blue]",
    ))


def sinc_api() -> None:
    """Sincroniza o banco local com a API da Caixa com barra de progresso."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=20),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task(
            "[cyan]A verificar API da Caixa...", total=100
        )

        def _callback(percentual: int, numero: int) -> None:
            progress.update(
                task,
                completed=percentual,
                description=f"[cyan]A baixar concurso #{numero}...",
            )

        sucesso, mensagem = baixar_dados_novos(callback_progresso=_callback)

    if sucesso:
        rprint(f"  [green]✔[/green]  {mensagem}")
    else:
        rprint(f"  [yellow]⚠[/yellow]  API: {mensagem}")


def _calcular_status(
    novo_ciclo: bool,
    faltantes: List[int],
    score_medio: float,
) -> Tuple[str, str]:
    """Devolve (texto_de_status, cor_rich) conforme o estado do ciclo."""
    if novo_ciclo:
        return "🔄  INÍCIO DE NOVO CICLO — Análise por Frequência", "cyan"
    n = len(faltantes)
    if n == 0:
        return "🔄  INÍCIO DE NOVO CICLO", "cyan"
    if n <= JANELA_OURO_MAX_FALTANTES and score_medio >= JANELA_OURO_MIN_SCORE:
        return "🏆  JANELA DE OURO ATIVA — APOSTA MÁXIMA", "bold magenta"
    if n <= JANELA_OURO_MAX_FALTANTES:
        return "🔥  FECHAMENTO DE CICLO PRÓXIMO", "bold red"
    return "✅  OPORTUNIDADE ESTATÍSTICA ATIVA", "green"


def exibir_dashboard(
    jogos:       List[Tuple[Concurso, float, int]],
    info:        Dict[str, Any],
    ultimo:      Concurso,
    alvo:        int,
    tempo_total: float,
) -> None:
    faltantes:   List[int] = info.get("dezenas_faltantes", [])
    novo_ciclo:  bool      = info.get("novo_ciclo", False)
    score_medio: float     = info.get("score_medio", 0.0)
    n_gerados:   int       = info.get("candidatos_gerados", 0)
    n_scored:    int       = info.get("candidatos_scored", 0)

    status_texto, status_cor = _calcular_status(novo_ciclo, faltantes, score_medio)

    if novo_ciclo:
        falt_str      = "Novo ciclo iniciado — todos os 25 já saíram"
        falt_contagem = "ciclo reiniciado"
    elif faltantes:
        falt_str      = ", ".join(f"{d:02d}" for d in faltantes)
        falt_contagem = f"{len(faltantes)} de 25"
    else:
        falt_str      = "Nenhum — ciclo fechado"
        falt_contagem = "0 de 25"

    # ── Painel de estratégia ──────────────────────────────────────────────
    console.print(Panel(
        f"[white]Status:[/white]          [{status_cor}]{status_texto}[/{status_cor}]\n"
        f"[white]Concurso alvo:[/white]   [bold white]#{alvo}[/bold white]  "
        f"(último registado: #{ultimo.numero} — {ultimo.data})\n"
        f"[white]Faltantes:[/white]       [bold yellow]{falt_str}[/bold yellow]  "
        f"({falt_contagem})\n"
        f"[white]Score médio:[/white]     [bold green]{score_medio:.6f}[/bold green]\n"
        f"[white]Performance:[/white]     {tempo_total:.2f}s  "
        f"({n_gerados} candidatos → {n_scored} pontuados)",
        title="[bold]Análise de Ciclo[/bold]",
        border_style="bright_black",
    ))

    # ── Tabela de jogos ───────────────────────────────────────────────────
    tabela = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
    )
    tabela.add_column("ID",                    justify="center", width=4)
    tabela.add_column("Dezenas Sugeridas",     width=45)
    tabela.add_column("Score V10",             justify="right",  width=12)
    tabela.add_column("Rep.",                  justify="center", width=5)

    faltantes_set = set(faltantes) if not novo_ciclo else set()

    for i, (jogo_obj, score, rep) in enumerate(jogos, 1):
        # Destaque visual: faltantes em amarelo, restantes em branco suave
        # Em novo_ciclo não há faltantes reais → todas as dezenas em branco
        partes = []
        for d in sorted(jogo_obj.dezenas):
            d_str = f"{d:02d}"
            if d in faltantes_set:
                partes.append(f"[bold yellow]{d_str}[/bold yellow]")
            else:
                partes.append(f"[dim white]{d_str}[/dim white]")
        dez_fmt = "  ".join(partes)

        # Janela de Ouro: não se aplica em novo ciclo (sem faltantes reais)
        janela_jogo = (
            not novo_ciclo
            and len(faltantes) <= JANELA_OURO_MAX_FALTANTES
            and score >= JANELA_OURO_MIN_SCORE
        )
        id_col = (
            "[bold magenta]★[/bold magenta]"
            if janela_jogo
            else f"[dim]{i:02d}[/dim]"
        )

        score_cor = "bold green" if score >= JANELA_OURO_MIN_SCORE else "white"

        tabela.add_row(
            id_col,
            dez_fmt,
            f"[{score_cor}]{score:.6f}[/{score_cor}]",
            str(rep),
        )

    console.print(tabela)
    console.print(
        f"  [dim]★ = Janela de Ouro (faltantes ≤ {JANELA_OURO_MAX_FALTANTES} "
        f"e score ≥ {JANELA_OURO_MIN_SCORE})[/dim]\n"
    )


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Timer inicia AQUI — mede o tempo total de parede (rede + CPU)
    t0: float = time.perf_counter()

    exibir_cabecalho()

    # 1. Sincronização com API da Caixa
    sinc_api()

    # 2. Carregamento — carregar_concursos() devolve List[Concurso] (nunca tuplas brutas)
    concursos: List[Concurso] = carregar_concursos()
    if not concursos:
        rprint("[bold red]ERRO:[/bold red] Base de dados vazia. "
               "Verifique a ligação à internet e tente novamente.")
        sys.exit(1)

    ultimo: Concurso = concursos[-1]
    alvo:   int      = ultimo.numero + 1
    rprint(f"  [green]✔[/green]  {len(concursos)} concurso(s) carregado(s) — "
           f"último: [bold]#{ultimo.numero}[/bold] ({ultimo.data})\n")

    # 3. Motor probabilístico
    engine: ProbabilisticEngine = ProbabilisticEngine()

    jogos: List[Tuple[Concurso, float, int]]
    info:  Dict[str, Any]

    with console.status("[bold yellow]⚙  A calcular jogos de elite..."):
        jogos, info = engine.gerar_jogos(concursos)

    # 4. Dashboard
    tempo_total: float = time.perf_counter() - t0   # perf_counter inclui I/O e rede
    exibir_dashboard(jogos, info, ultimo, alvo, tempo_total)

    # 5. Persistência
    engine.salvar_historico_v10(jogos, alvo)
    rprint(f"  [dim]✔ Dados registados em historico_v10.txt[/dim]\n")


if __name__ == "__main__":
    main()
