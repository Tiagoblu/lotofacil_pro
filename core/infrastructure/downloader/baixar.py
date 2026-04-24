# core/infrastructure/downloader/baixar.py
#
# Responsável por sincronizar o banco local com a API oficial da Caixa.
# Usa exclusivamente as funções do database.py já existente no projecto.
# Não depende de nenhum Repository externo.

import time
from typing import Callable, Optional, Tuple

import requests

from core.domain.models import Concurso
from core.infrastructure.database.database import (
    carregar_concursos,
    inserir_concurso,
)

# ── Endpoint oficial ────────────────────────────────────────────────────────
URL_API: str = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

# ── Parâmetros de rede ──────────────────────────────────────────────────────
TIMEOUT_SEGUNDOS:     int   = 15    # tempo máximo por request
MAX_TENTATIVAS:       int   = 3     # retries por concurso em caso de falha
DELAY_ENTRE_REQUESTS: float = 0.4  # pausa entre downloads bem-sucedidos (anti rate-limit)
DELAY_RETRY:          float = 2.0  # pausa antes de re-tentativa após falha

# ── Controlo de cancelamento ────────────────────────────────────────────────
_cancelar: bool = False


def solicitar_cancelamento() -> None:
    """Sinaliza ao loop de download que deve parar na próxima iteração."""
    global _cancelar
    _cancelar = True


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS INTERNOS
# ══════════════════════════════════════════════════════════════════════════

def _obter_ultimo_numero_local() -> int:
    """
    Devolve o número do concurso mais recente no banco local.
    Usa carregar_concursos() do database.py — não depende de nenhum Repository.
    Devolve 0 se o banco estiver vazio.
    """
    concursos = carregar_concursos()
    return concursos[-1].numero if concursos else 0


def _obter_ultimo_numero_remoto() -> int:
    """
    Consulta a API sem número de concurso para obter o total actual.
    Lança Exception em caso de falha de rede ou resposta inesperada.
    """
    response = requests.get(URL_API, timeout=TIMEOUT_SEGUNDOS)
    response.raise_for_status()
    dados = response.json()
    numero = dados.get("numero")
    if not numero:
        raise ValueError(f"Campo 'numero' ausente na resposta da API: {dados}")
    return int(numero)


def _baixar_concurso(numero: int) -> Concurso:
    """
    Baixa e converte um concurso específico da API.
    Lança Exception se o concurso não puder ser obtido.
    """
    url = f"{URL_API}/{numero}"
    response = requests.get(url, timeout=TIMEOUT_SEGUNDOS)
    response.raise_for_status()
    dados = response.json()

    return Concurso(
        numero=int(dados["numero"]),
        data=str(dados["dataApuracao"]),
        dezenas=tuple(int(d) for d in dados["listaDezenas"]),
    )


# ══════════════════════════════════════════════════════════════════════════
#  API PÚBLICA
# ══════════════════════════════════════════════════════════════════════════

def baixar_dados_novos(
    callback_progresso: Optional[Callable[[int, int], None]] = None,
) -> Tuple[bool, str]:
    """
    Sincroniza o banco local com a API da Caixa.

    1. Obtém o último número local e o último número remoto.
    2. Para cada concurso em falta, tenta até MAX_TENTATIVAS vezes.
    3. Insere cada concurso descarregado com inserir_concurso().
    4. Chama callback_progresso(percentual_0_100, numero_actual) a cada inserção.

    Args:
        callback_progresso: função opcional chamada após cada download bem-sucedido.
                            recebe (percentual: int, numero_do_concurso: int).

    Returns:
        Tuple[bool, str] — (sucesso, mensagem_para_o_utilizador)
    """
    global _cancelar
    _cancelar = False

    # ── Último local ────────────────────────────────────────────────────
    ultimo_local: int = _obter_ultimo_numero_local()

    # ── Último remoto ───────────────────────────────────────────────────
    try:
        ultimo_remoto: int = _obter_ultimo_numero_remoto()
    except Exception as exc:
        return False, f"Erro ao conectar com a API da Caixa: {exc}"

    if ultimo_local >= ultimo_remoto:
        return True, f"Banco já actualizado (concurso #{ultimo_remoto})."

    # ── Download ────────────────────────────────────────────────────────
    total_para_baixar: int = ultimo_remoto - ultimo_local
    baixados: int = 0

    for numero in range(ultimo_local + 1, ultimo_remoto + 1):

        if _cancelar:
            return False, f"Download cancelado. {baixados} concurso(s) guardado(s)."

        sucesso_concurso: bool = False

        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                concurso = _baixar_concurso(numero)
                inserir_concurso(concurso)          # usa database.py existente
                sucesso_concurso = True
                break
            except Exception as exc:
                if tentativa < MAX_TENTATIVAS:
                    time.sleep(DELAY_RETRY)
                else:
                    return False, (
                        f"Falha ao baixar concurso #{numero} "
                        f"após {MAX_TENTATIVAS} tentativas: {exc}"
                    )

        if not sucesso_concurso:
            # Nunca deve chegar aqui, mas mantém a invariante
            return False, f"Erro inesperado no concurso #{numero}."

        baixados += 1
        percentual: int = int((baixados / total_para_baixar) * 100)

        if callback_progresso:
            callback_progresso(percentual, numero)

        # Anti rate-limit: pausa entre cada download bem-sucedido
        if numero < ultimo_remoto:
            time.sleep(DELAY_ENTRE_REQUESTS)

    return True, f"{baixados} concurso(s) descarregado(s) com sucesso."
