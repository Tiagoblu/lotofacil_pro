# infrastructure/database/repository.py

from typing import List, Optional
from core.infrastructure.database.database import get_connection
from core.domain.models import Concurso


class ConcursoRepository:

    @staticmethod
    def salvar(concurso: Concurso) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO concursos (
                numero, data,
                d1, d2, d3, d4, d5,
                d6, d7, d8, d9, d10,
                d11, d12, d13, d14, d15
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            concurso.numero,
            concurso.data,
            *concurso.dezenas
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def obter_por_numero(numero: int) -> Optional[Concurso]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT numero, data,
                   d1, d2, d3, d4, d5,
                   d6, d7, d8, d9, d10,
                   d11, d12, d13, d14, d15
            FROM concursos
            WHERE numero = ?
        """, (numero,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        numero, data, *dezenas = row

        return Concurso(numero=numero, data=data, dezenas=tuple(dezenas))

    @staticmethod
    def obter_todos() -> List[Concurso]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT numero, data,
                   d1, d2, d3, d4, d5,
                   d6, d7, d8, d9, d10,
                   d11, d12, d13, d14, d15
            FROM concursos
            ORDER BY numero ASC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [
            Concurso(numero=row[0], data=row[1], dezenas=tuple(row[2:]))
            for row in rows
        ]

    @staticmethod
    def obter_ultimo() -> Optional[Concurso]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT numero, data,
                   d1, d2, d3, d4, d5,
                   d6, d7, d8, d9, d10,
                   d11, d12, d13, d14, d15
            FROM concursos
            ORDER BY numero DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Concurso(numero=row[0], data=row[1], dezenas=tuple(row[2:]))