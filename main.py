import os
import sys

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

def main():
    print("="*65)
    print("       LOTOFÁCIL PRO V11 – Inteligência de Decisão")
    print("="*65)

    try:
        engine = ProbabilisticEngine()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM concursos ORDER BY numero ASC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("Banco de dados vazio.")
            return

        concursos = [Concurso(r[0], r[1], tuple(r[2:17])) for r in rows]
        ultimo_concurso = concursos[-1]
        alvo = ultimo_concurso.numero + 1

        # Gera os jogos usando o motor probabilístico
        jogos, info = engine.gerar_jogos(concursos)
        faltantes = info.get('dezenas_faltantes', [])

        # RESTAURAÇÃO: Painel de Estratégia e Fechamento de Ciclo
        if len(faltantes) <= 3 and len(faltantes) > 0:
            status = "🔥 JANELA DE OURO (Fechamento Próximo)"
        elif len(faltantes) == 0:
            status = "🔄 INÍCIO DE NOVO CICLO"
        else:
            status = "✅ OPORTUNIDADE ESTATÍSTICA"

        print(f"STATUS DA ESTRATÉGIA : {status}")
        print("-" * 65)
        print(f"Último Registrado: {ultimo_concurso.numero}  |  Alvo: {alvo}")
        print(f"Faltantes no Ciclo: {' '.join(f'{d:02d}' for d in faltantes)}")
        print("-" * 65)

        print(f"\nJOGOS SUGERIDOS PARA O CONCURSO {alvo}:")
        for i, (jogo_obj, score, rep) in enumerate(jogos, 1):
            dezenas_puras = jogo_obj.dezenas if hasattr(jogo_obj, 'dezenas') else jogo_obj
            dez_fmt = " ".join(f"{d:02d}" for d in sorted(dezenas_puras))
            print(f"Jogo {i}: {dez_fmt} | Score: {score:.6f}")

        if hasattr(engine, 'salvar_historico_v10'):
            engine.salvar_historico_v10(jogos, alvo)
            print(f"\n[OK] Sugestões registradas no histórico V10 com sucesso.")

    except Exception as e:
        print(f"\n[ERRO DE EXECUÇÃO]: {e}")

if __name__ == "__main__":
    main()