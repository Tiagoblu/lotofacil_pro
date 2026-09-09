import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# Configuração Inicial da Página Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lotofácil Pro V10",
    page_icon="🎯",
    layout="wide"
)

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

# -----------------------------------------------------------------------------
# Funções Auxiliares e Métricas
# -----------------------------------------------------------------------------
def carregar_ultimo_resultado(caminho_historico="historico_v10.txt"):
    """Carrega o último concurso cadastrado no arquivo de histórico."""
    if not os.path.exists(caminho_historico):
        return [3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 16, 18, 19, 21, 25]
    
    ultimo_resultado = []
    try:
        with open(caminho_historico, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()
            for linha in reversed(linhas):
                if "Resultado:" in linha:
                    partes = linha.split("Resultado:")[1].strip().split()
                    ultimo_resultado = [int(x) for x in partes]
                    break
    except Exception:
        pass
        
    return ultimo_resultado if len(ultimo_resultado) == 15 else [3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 16, 18, 19, 21, 25]

def calcular_score_v10(jogo, ultimo_resultado):
    """Calcula a pontuação V10 baseada nos padrões estatísticos do jogo."""
    repeticoes = len(set(jogo) & set(ultimo_resultado))
    pares = sum(1 for d in jogo if d % 2 == 0)
    primos = sum(1 for d in jogo if d in PRIMOS)
    soma = sum(jogo)
    
    score = 1.0
    
    # Filtro de repetição com o último resultado (ideal: 8, 9 ou 10)
    if repeticoes in [8, 9, 10]:
        score += 0.15
    elif repeticoes in [7, 11]:
        score += 0.05
    else:
        score -= 0.20
        
    # Balanceamento de Pares e Ímpares (ideal: 7 ou 8 pares)
    if pares in [7, 8]:
        score += 0.10
    elif pares in [6, 9]:
        score += 0.03
        
    # Números Primos (ideal: 5 ou 6)
    if primos in [5, 6]:
        score += 0.08
        
    # Faixa da Soma Total (ideal: 180 a 220)
    if 180 <= soma <= 220:
        score += 0.07
        
    return round(score, 6), repeticoes

def gerar_apostas_v10(qtd_solicitada, ultimo_resultado, controle_diversidade=True):
    """Gera até 100 apostas aplicando os filtros V10 e a trava de diversidade."""
    apostas = []
    jogos_set = set()
    freq_dezenas = {i: 0 for i in range(1, 26)}
    
    max_tentativas = 200000
    tentativas = 0
    
    # Teto proporcional de presença para cada dezena no lote de apostas
    teto_frequencia = int(qtd_solicitada * 0.72) + 2 if controle_diversidade and qtd_solicitada >= 10 else qtd_solicitada
    
    while len(apostas) < qtd_solicitada and tentativas < max_tentativas:
        tentativas += 1
        candidato = tuple(sorted(random.sample(range(1, 26), 15)))
        
        if candidato in jogos_set:
            continue
            
        score, repeticoes = calcular_score_v10(candidato, ultimo_resultado)
        
        # Filtro de qualidade mínima do Score
        if score < 0.95:
            continue
            
        # Regra de controle de diversidade (impede concentração excessiva em poucas dezenas)
        if controle_diversidade and len(apostas) >= 5:
            excede_teto = any(freq_dezenas[d] >= teto_frequencia for d in candidato)
            if excede_teto and random.random() < 0.85:
                continue
                
        jogos_set.add(candidato)
        for d in candidato:
            freq_dezenas[d] += 1
            
        apostas.append({
            "Dezenas_Tuple": candidato,
            "Dezenas Sugeridas (15 números)": " ".join(f"{d:02d}" for d in candidato),
            "Score V10": score,
            "Repetições": repeticoes
        })
        
    # Ordena pelo Score V10 do maior para o menor
    apostas = sorted(apostas, key=lambda x: x["Score V10"], reverse=True)
    for idx, item in enumerate(apostas, 1):
        item["ID"] = idx
        
    return apostas, freq_dezenas

def salvar_historico_v10(apostas, caminho_historico="historico_v10.txt"):
    """Registra a nova execução no arquivo de log de histórico."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    bloco = ["\n--------------------------------------------------------------------------------"]
    bloco.append(f"Execução em: {agora}")
    bloco.append("Sugestões para o Concurso Alvo: 3780")
    bloco.append("")
    
    for item in apostas:
        bloco.append(f"Jogo {item['ID']}: {item['Dezenas Sugeridas (15 números)']}")
        bloco.append(f"  Score V10             : {item['Score V10']:.6f}")
        bloco.append(f"  Repetições Anteriores : {item['Repetições']}")
        bloco.append("")
        
    try:
        with open(caminho_historico, "a", encoding="utf-8") as f:
            f.write("\n".join(bloco) + "\n")
    except Exception as e:
        st.warning(f"Não foi possível atualizar o histórico local: {e}")

# -----------------------------------------------------------------------------
# Interface do Usuário (Streamlit UI)
# -----------------------------------------------------------------------------
st.title("🎯 Lotofácil Pro - Gerador de Apostas V10")
st.markdown("Gerador otimizado com filtro estatístico V10 e controle de diversidade de dezenas.")

ultimo_resultado = carregar_ultimo_resultado()

# Painel Lateral
st.sidebar.header("Parâmetros de Geração")

qtd_apostas = st.sidebar.number_input(
    "Quantidade de apostas (1 a 100):",
    min_value=1,
    max_value=100,
    value=30,
    step=1
)

aplicar_diversidade = st.sidebar.checkbox(
    "Ativar Controle de Diversidade",
    value=True,
    help="Equilibra a distribuição das dezenas entre 1 e 25 para evitar repetição excessiva em volumes grandes de jogos."
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Último resultado base:**\n`{' '.join(f'{d:02d}' for d in ultimo_resultado)}`")

# Ação Principal
if st.sidebar.button("🚀 Gerar Apostas V10", use_container_width=True):
    with st.spinner("Processando combinações e aplicando estatísticas V10..."):
        apostas, frequencias = gerar_apostas_v10(qtd_apostas, ultimo_resultado, aplicar_diversidade)
        
        # Converte para DataFrame
        df_exibicao = pd.DataFrame(apostas)[["ID", "Dezenas Sugeridas (15 números)", "Score V10", "Repetições"]]
        
        # Salva a execução no histórico
        salvar_historico_v10(apostas)
        
        # Exibe Métricas Resumidas
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Apostas Geradas", len(apostas))
        col2.metric("Score V10 Médio", f"{df_exibicao['Score V10'].mean():.4f}")
        col3.metric("Repetição Média", f"{df_exibicao['Repetições'].mean():.1f} dezenas")
        
        st.markdown("---")
        
        # Tabela de Resultados
        st.subheader("📋 Jogos Gerados")
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Dezenas Sugeridas (15 números)": st.column_config.TextColumn("Dezenas Sugeridas (15 números)", width="large"),
                "Score V10": st.column_config.NumberColumn("Score V10", format="%.6f"),
                "Repetições": st.column_config.NumberColumn("Repetições Anteriores"),
            }
        )
        
        # Download do CSV
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
        nome_arquivo = f"{timestamp}_export.csv"
        csv_data = df_exibicao.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Baixar Arquivo CSV das Apostas",
            data=csv_data,
            file_name=nome_arquivo,
            mime="text/csv",
            use_container_width=True
        )
        
        # Gráfico/Tabela de Frequência das Dezenas
        st.markdown("---")
        st.subheader("📊 Distribuição das Dezenas Geradas (1 a 25)")
        
        df_freq = pd.DataFrame({
            "Dezena": [f"{i:02d}" for i in range(1, 26)],
            "Frequência": [frequencias[i] for i in range(1, 26)],
            "Porcentagem (%)": [round((frequencias[i] / len(apostas)) * 100, 1) for i in range(1, 26)]
        })
        
        st.dataframe(
            df_freq.T,
            use_container_width=True
        )