import os
import sys

# 1. Aponta para a raiz do projeto para achar a pasta 'core'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2. Usa a conexão oficial do SEU sistema (evita criar banco falso)
try:
    from core.infrastructure.database.database import get_connection
except ImportError as e:
    print(f"Erro ao importar a conexão oficial: {e}")
    sys.exit(1)

# 3. Dados do concurso
CONCURSO = 3666
DATA = "22/04/2026" 
DEZENAS = [1, 4, 6, 7, 9, 12, 14, 15, 16, 17, 19, 20, 21, 22, 23]

def forcar_atualizacao():
    # Usa a função nativa do seu projeto para conectar no lugar certo
    conn = get_connection() 
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO concursos 
            (numero, data, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (CONCURSO, DATA, *sorted(DEZENAS)))
        
        conn.commit()
        print(f"\n✅ SUCESSO: Concurso {CONCURSO} integrado ao banco de dados oficial do sistema!")
        print(f"Resultado registrado: {sorted(DEZENAS)}")
        print("\nAgora você pode rodar o 'py main.py' que o alvo será o 3667.")
    except Exception as e:
        print(f"❌ ERRO AO INSERIR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    forcar_atualizacao()