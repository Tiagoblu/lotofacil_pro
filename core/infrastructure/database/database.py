# core/infrastructure/database/database.py
#
# Camada de infraestrutura — SQLite → modelos de domínio
# ───────────────────────────────────────────────────────
# NUNCA devolve tuplas brutas para fora deste módulo.
# Toda a conversão SQLite → Concurso acontece aqui.

import sqlite3
from pathlib import Path
from typing import List, Optional

from core.domain.models import Concurso

# ── Caminho do banco ───────────────────────────────────────────────────────
# parents[3] sobe: database.py → database/ → infrastructure/ → core/ → raiz
BASE_DIR: Path = Path(__file__).resolve().parents[3]
DB_PATH:  Path = BASE_DIR / "database" / "lotofacil.db"

# ── SQL explícito (não usa SELECT * para não depender da ordem das colunas) ─
_SQL_SELECT = (
    "SELECT numero, data, "
    "d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15 "
    "FROM concursos"
)


# ══════════════════════════════════════════════════════════════════════════
#  CONEXÃO
# ══════════════════════════════════════════════════════════════════════════

def get_connection() -> sqlite3.Connection:
    """Devolve uma conexão SQLite garantindo que a pasta existe."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")   # melhor desempenho em leitura
    return conn


# ══════════════════════════════════════════════════════════════════════════
#  CONVERSÃO INTERNA  (tupla SQLite → modelo de domínio)
# ══════════════════════════════════════════════════════════════════════════

def _row_to_concurso(row: tuple) -> Concurso:
    """
    Converte uma linha (numero, data, d1..d15) num objeto Concurso.
    row[0]  = numero  (int)
    row[1]  = data    (str)
    row[2:] = d1-d15  (15 ints)
    """
    return Concurso(
        numero=int(row[0]),
        data=str(row[1]),
        dezenas=tuple(int(d) for d in row[2:17]),
    )


# ══════════════════════════════════════════════════════════════════════════
#  LEITURA  →  sempre devolve List[Concurso], nunca tuplas brutas
# ══════════════════════════════════════════════════════════════════════════

def carregar_concursos() -> List[Concurso]:
    """
    Carrega todos os concursos ordenados por número crescente.

    Returns:
        List[Concurso] — pronto a passar directamente ao motor.

    Raises:
        sqlite3.OperationalError: se a tabela não existir.
        SystemExit: não faz sys.exit — deixa o chamador decidir.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"{_SQL_SELECT} ORDER BY numero ASC")
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [_row_to_concurso(row) for row in rows]


def carregar_ultimos_n(n: int) -> List[Concurso]:
    """
    Carrega os N concursos mais recentes, ordenados do mais antigo ao mais recente.
    Útil para análise de janela móvel sem carregar todo o histórico.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"{_SQL_SELECT} ORDER BY numero DESC LIMIT ?", (n,))
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [_row_to_concurso(row) for row in reversed(rows)]


def carregar_por_numero(numero: int) -> Optional[Concurso]:
    """Devolve o Concurso com o número dado, ou None se não existir."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"{_SQL_SELECT} WHERE numero = ? LIMIT 1", (numero,))
        row = cursor.fetchone()
    finally:
        conn.close()

    return _row_to_concurso(row) if row is not None else None


# ══════════════════════════════════════════════════════════════════════════
#  ESCRITA
# ══════════════════════════════════════════════════════════════════════════

def inserir_concurso(concurso: Concurso) -> None:
    """Insere um Concurso. Ignora silenciosamente se o número já existir."""
    sql = (
        "INSERT OR IGNORE INTO concursos "
        "(numero, data, d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )
    valores = (concurso.numero, concurso.data, *concurso.dezenas)
    conn = get_connection()
    try:
        conn.execute(sql, valores)
        conn.commit()
    finally:
        conn.close()


def inserir_lote(concursos: List[Concurso]) -> int:
    """
    Insere uma lista de Concursos em bloco (executemany).

    Returns:
        Número de linhas efectivamente inseridas.
    """
    sql = (
        "INSERT OR IGNORE INTO concursos "
        "(numero, data, d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    )
    dados = [(c.numero, c.data, *c.dezenas) for c in concursos]
    conn = get_connection()
    try:
        cursor = conn.executemany(sql, dados)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════
#  DDL — inicialização do esquema
# ══════════════════════════════════════════════════════════════════════════

def criar_tabelas() -> None:
    """Cria a tabela 'concursos' se ainda não existir (idempotente)."""
    ddl = """
        CREATE TABLE IF NOT EXISTS concursos (
            numero  INTEGER PRIMARY KEY,
            data    TEXT,
            d1  INTEGER, d2  INTEGER, d3  INTEGER, d4  INTEGER, d5  INTEGER,
            d6  INTEGER, d7  INTEGER, d8  INTEGER, d9  INTEGER, d10 INTEGER,
            d11 INTEGER, d12 INTEGER, d13 INTEGER, d14 INTEGER, d15 INTEGER
        )
    """
    conn = get_connection()
    try:
        conn.execute(ddl)
        conn.commit()
    finally:
        conn.close()


def inicializar_banco() -> None:
    """Alias público para criar_tabelas(). Seguro para chamar na startup."""
    criar_tabelas()
