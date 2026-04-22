import os
import sys

# 1. Ajuste de Path Absoluto para o ambiente do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from core.infrastructure.database.database import get_connection
    from core.engine.probabilistic_engine import ProbabilisticEngine
    from core.domain.models import Concurso
except ImportError as e:
    print(f"\n[ERRO DE ESTRUTURA]: {e}")
    sys.exit(1)

def preparar_concursos():
    """Busca dados no DB e converte para a lista de objetos Concurso exigida pelo motor."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Busca: numero(0), data(1), d1(2)...d15(16)
        cursor.execute("SELECT * FROM concursos ORDER BY numero ASC")
        rows = cursor.fetchall()
        
        concursos_obj = []
        for r in rows:
            # Converte a fatia d1-d15 (índices 2 a 16) para a tupla do modelo
            obj = Concurso(
                numero=r[0],
                data=r[1],
                dezenas=tuple(r[2:17])
            )
            concursos_obj.append(obj)
        return concursos_obj
    except Exception as e:
        print(f"[ERRO NO BANCO]: {e}")
        return []
    finally:
        conn.close()

def main():
    print("="*65)
    print("       LOTOFÁCIL PRO V11 – Inteligência de Decisão")
    print("="*65)

    try:
        # 1. Prepara os dados no formato que o motor espera (List[Concurso])
        lista_concursos = preparar_concursos()
        if not lista_concursos:
            print("[ERRO]: Falha ao carregar dados do banco.")
            return

        ultimo_concurso = lista_concursos[-1]
        alvo = ultimo_concurso.numero + 1

        # 2. Inicializa o motor e processa a geração
        engine = ProbabilisticEngine()
        
        # O retorno do motor é: (lista_de_jogos_avaliados, info_ciclo)
        # Onde cada item em lista_de_jogos_avaliados é (Concurso, score, repeticoes)
        jogos_brutos, info_ciclo = engine.gerar_jogos(
            concursos=lista_concursos, 
            quantidade=5, 
            modo="HIBRIDO_V9"
        )

        # 3. Inteligência 'Janela de Ouro'
        faltantes = info_ciclo.get('dezenas_faltantes', [])
        score_lider = jogos_brutos[0][1] # Pega o score do primeiro jogo da lista
        
        if 0 < len(faltantes) <= 4 and score_lider >= 1.18:
            status = "🔥 JANELA DE OURO"
            conselho = f"Momento de máxima probabilidade para o concurso {alvo}."
        elif len(faltantes) <= 6:
            status = "✅ OPORTUNIDADE ALTA"
            conselho = "Fechamento de ciclo iminente detectado."
        else:
            status = "⚖️ ESTÁVEL"
            conselho = "Análise estatística de rotina."

        # 4. Dashboard de Saída
        print(f"STATUS DA ESTRATÉGIA : {status}")
        print(f"CONSELHO DO SISTEMA  : {conselho}")
        print("-" * 65)
        print(f"Último Registrado: {ultimo_concurso.numero}  |  Alvo: {alvo}")
        print(f"Faltantes no Ciclo: {' '.join(map(str, faltantes))}")
        print("-" * 65)

        print(f"\nJOGOS SUGERIDOS PARA O CONCURSO {alvo}:")
        
        # Descompacta a tupla (ObjetoConcurso, Score, Repeticoes)
        for i, (jogo_obj, score, rep) in enumerate(jogos_brutos, 1):
            dezenas_fmt = " ".join(f"{d:02d}" for d in sorted(jogo_obj.dezenas))
            print(f"Jogo {i}: {dezenas_fmt} | Score V10: {score:.6f}")

        # 5. Salva histórico (O motor espera a lista de tuplas avaliadas)
        engine.salvar_historico_v10(jogos_brutos, arquivo="historico_v10.txt")
        print("\n[OK] Processamento concluído com sucesso.")

    except Exception as e:
        print(f"\n[ERRO NA EXECUÇÃO]: {e}")

if __name__ == "__main__":
    main()