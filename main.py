import os
import sys
from core.engine.probabilistic_engine import ProbabilisticEngine
from core.database.db_manager import DBManager
from core.utils.scanner import ScannerIntegridade # Assumindo a estrutura do seu scanner

# ============================================================
# CONFIGURAÇÕES DA VERSÃO V11
# ============================================================
VERSAO = "V11 – Inteligência de Decisão"
VOLATILIDADE_ATUAL = 0.0035
PESO_RECENCIA = 0.25

def gerar_conselho_v11(faltantes, score_jogo_1):
    """
    Analisa matematicamente a janela de oportunidade baseada no 
    estado do ciclo e na força do Score V10.
    """
    num_faltantes = len(faltantes)
    
    if num_faltantes <= 3 and score_jogo_1 >= 1.20:
        nivel = "🔥 MÁXIMA (JANELA DE OURO)"
        conselho = "O ciclo está para fechar e o Score V10 está altíssimo. Momento ideal para buscar premiações superiores."
    elif num_faltantes <= 5:
        nivel = "✅ ALTA"
        conselho = "Fase final de ciclo. As dezenas faltantes têm altíssima probabilidade de sorteio conjunto."
    elif num_faltantes > 20:
        nivel = "⚖️ MODERADA (INÍCIO DE CICLO)"
        conselho = "Início de novo ciclo. O motor está calibrando as novas tendências. Mantenha apostas base."
    else:
        nivel = "⚠️ ESTÁVEL"
        conselho = "Meio de ciclo. O sistema busca o equilíbrio entre dezenas repetidas e atrasadas."

    return nivel, conselho

def main():
    print("="*60)
    print(f"==== LotoFácil Pro {VERSAO} ====")
    print("="*60)

    # 1. Sincronização e Integridade
    db = DBManager()
    scanner = ScannerIntegridade(db)
    scanner.executar_sincronizacao_total() # Garante histórico 100% linear

    # 2. Inicialização do Motor
    engine = ProbabilisticEngine(db)
    
    # 3. Coleta de Dados do Ciclo
    ultimo_concurso = db.get_ultimo_concurso_id()
    faltantes = engine.get_dezenas_faltantes_ciclo()
    
    # 4. Geração de Jogos
    # Usando o modo HIBRIDO_V9 conforme definido na arquitetura
    jogos_sugeridos = engine.gerar_jogos(
        quantidade=5, 
        modo="HIBRIDO_V9", 
        volatilidade=VOLATILIDADE_ATUAL,
        peso_recencia=PESO_RECENCIA
    )

    # 5. Cálculo do Conselho V11
    score_lider = jogos_sugeridos[0]['score']
    nivel_op, texto_conselho = gerar_conselho_v11(faltantes, score_lider)

    # 6. Dashboard de Saída
    print(f"\nÚltimo no banco: {ultimo_concurso} | Status do Ciclo: {engine.get_status_ciclo()}")
    print(f"Faltantes ({len(faltantes)}): {' '.join(map(str, sorted(faltantes)))}")
    
    print("-" * 60)
    print(f"INDICADOR DE OPORTUNIDADE: {nivel_op}")
    print(f"CONSELHO ESTRATÉGICO: {texto_conselho}")
    print("-" * 60)

    print("\nJOGOS PARA O PRÓXIMO CONCURSO:")
    for i, jogo in enumerate(jogos_sugeridos, 1):
        dezenas_str = " ".join(f"{d:02d}" for d in sorted(jogo['dezenas']))
        print(f"Jogo {i}: {dezenas_str} | Score: {jogo['score']:.6f}")

    # 7. Salvamento de Log
    engine.salvar_historico_v10(jogos_sugeridos, arquivo="historico_v10.txt")
    print("\n[OK] Histórico atualizado e jogos salvos.")

if __name__ == "__main__":
    main()