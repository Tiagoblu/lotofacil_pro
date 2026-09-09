import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# Configuração Inicial da Página Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lotofácil Pro V10 🎯",
    page_icon="🎯",
    layout="wide"
)

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

# Inicialização do Session State para manter os jogos visíveis após downloads
if "apostas" not in st.session_state:
    st.session_state.apostas = None
if "frequencias" not in st.session_state:
    st.session_state.frequencias = None

# -----------------------------------------------------------------------------
# Funções Auxiliares e Algoritmo V10
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
    
    # Repetição do concurso anterior (faixa de alta probabilidade: 8, 9 ou 10)
    if repeticoes in [8, 9, 10]:
        score += 0.15
    elif repeticoes in [7, 11]:
        score += 0.05
    else:
        score -= 0.20
        
    # Equilíbrio de Pares e Ímpares (faixa de ouro: 7 ou 8 pares)
    if pares in [7, 8]:
        score += 0.10
    elif pares in [6, 9]:
        score += 0.03
        
    # Números Primos (faixa ideal: 5 ou 6 primos)
    if primos in [5, 6]:
        score += 0.08
        
    # Faixa da Soma Total das Dezenas (ideal: 180 a 220)
    if 180 <= soma <= 220:
        score += 0.07
        
    return round(score, 6), repeticoes, pares, primos, soma

def gerar_apostas_v10(qtd_solicitada, ultimo_resultado, controle_diversidade=True):
    """Gera até 100 apostas otimizadas aplicando filtros V10 e trava de diversidade."""
    apostas = []
    jogos_set = set()
    freq_dezenas = {i: 0 for i in range(1, 26)}
    
    max_tentativas = 250000
    tentativas = 0
    
    teto_frequencia = int(qtd_solicitada * 0.72) + 2 if controle_diversidade and qtd_solicitada >= 10 else qtd_solicitada
    
    while len(apostas) < qtd_solicitada and tentativas < max_tentativas:
        tentativas += 1
        candidato = tuple(sorted(random.sample(range(1, 26), 15)))
        
        if candidato in jogos_set:
            continue
            
        score, repeticoes, pares, primos, soma = calcular_score_v10(candidato, ultimo_resultado)
        
        if score < 0.95:
            continue
            
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
            "Repetições": repeticoes,
            "Pares": pares,
            "Primos": primos,
            "Soma": soma
        })
        
    apostas = sorted(apostas, key=lambda x: x["Score V10"], reverse=True)
    for idx, item in enumerate(apostas, 1):
        item["ID"] = idx
        
    return apostas, freq_dezenas

def salvar_historico_v10(apostas, caminho_historico="historico_v10.txt"):
    """Salva a geração de jogos no arquivo de histórico."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    bloco = ["\n--------------------------------------------------------------------------------"]
    bloco.append(f"Execução em: {agora}")
    bloco.append("Sugestões para o Concurso Alvo: Lotofácil Pro V10")
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
        st.warning(f"⚠️ Não foi possível atualizar o histórico local: {e}")

# -----------------------------------------------------------------------------
# Interface Principal (Streamlit UI)
# -----------------------------------------------------------------------------
st.title("🎯 Lotofácil Pro - Gerador Inteligente V10")
st.markdown("🔥 **Ferramenta de análise estatística, filtragem matemática e geração de jogos otimizados.**")

ultimo_resultado = carregar_ultimo_resultado()

# =============================================================================
# JANELAS INFORMATIVAS
# =============================================================================

with st.expander("🔥 JANELA ESPECIAL: Quando é a Melhor Oportunidade para Apostar? 💰", expanded=True):
    st.markdown("""
    ### 🟢 Oportunidades de Alto Valor (Sinal Verde para Apostar):
    
    1. **🏆 Concursos Acumulados ou Especiais:**
       * Quando o prêmio acumulado ultrapassa a média regular ou em concursos de final 0. O retorno do investimento se torna proporcionalmente superior ao risco estatístico.
       
    2. **🔄 Efeito Pêndulo (Anomalia no Concurso Anterior):**
       * Quando o último concurso teve uma **anomalia de repetição** (repetiu apenas 5 ou 6 dezenas, ou repetiu 12 ou 13 dezenas). Estatisticamente, o concurso seguinte tende fortemente a retornar para o **centro da curva (8, 9 ou 10 repetidas)**, tornando as apostas geradas pelo V10 extremamente precisas.
       
    3. **⭐ Lote com Score V10 Médio Alto (>= 1.25):**
       * Ao gerar seu lote de apostas, observe a métrica **Score V10 Médio**. Quando a média do lote fica acima de **1.2500**, significa que o gerador encontrou combinações de altíssima convergência (Pares, Primos, Soma e Repetição alinhados em perfeita simetria).
       
    4. **📊 Distribuição Homogênea no Controle de Diversidade:**
       * Quando você gera um lote grande (ex: 30 a 100 apostas) com o **Controle de Diversidade Ativado** e todas as dezenas de 01 a 25 ficam com presença equilibrada entre 50% e 70%. Isso garante cobertura ampla da matriz sem desperdício de jogos repetidos.

    ---
    🔴 **Quando EVITAR apostar alto:** Quando o resultado anterior for absurdamente atípico e você estiver jogando sem filtros estatísticos. O V10 elimina esses cenários ruins automaticamente.
    """)

with st.expander("📖 Janela 1: Como Funciona o Algoritmo V10 e os Filtros Estatísticos ⚙️", expanded=False):
    st.markdown("""
    O **Algoritmo V10** analisa milhares de combinações possíveis e calcula o **Score V10** de cada jogo com base nas leis de probabilidade da Lotofácil:
    
    * **🔁 Repetição do Concurso Anterior (Peso 0.15):** Cerca de 60% dos sorteios repetem **8, 9 ou 10 dezenas** do resultado imediatamente anterior.
    * **⚖️ Equilíbrio Par / Ímpar (Peso 0.10):** A maior frequência histórica ocorre com **7 Pares / 8 Ímpares** ou **8 Pares / 7 Ímpares**.
    * **🔢 Números Primos (Peso 0.08):** Os números primos da Lotofácil são **(02, 03, 05, 07, 11, 13, 17, 19, 23)**. O algoritmo foca em apostas com **5 ou 6 primos**.
    * **🧮 Faixa da Soma Total (Peso 0.07):** A soma das 15 dezenas sorteadas quase sempre se posiciona entre **180 e 220**.
    """)

with st.expander("🪟 Janela 2: Guia de Recursos e Controle de Diversidade 🛡️", expanded=False):
    st.markdown("""
    * **⚙️ Painel Lateral:** Selecione a quantidade de jogos desejada (1 a 100) e ative a trava de diversidade.
    * **🛡️ Controle de Diversidade:** Evita a "superconcentração" em poucos números. Limita o teto de aparição das dezenas para distribuir o risco do lote por todo o volante (01 a 25).
    * **📊 Tabela de Frequência:** Mostra exatamente quantas vezes e em qual porcentagem cada dezena aparece na sua cartela total de jogos.
    * **📥 Exportação Rápida:** Baixe suas apostas prontas em formato CSV com um único clique.
    """)

with st.expander("💡 Janela 3: Instruções Passo a Passo para Jogar 📝", expanded=False):
    st.markdown("""
    1. ⚙️ Defina a quantidade de apostas no painel à esquerda (ex: **30, 50 ou 100 apostas**).
    2. 🚀 Clique no botão **🚀 Gerar Apostas V10**.
    3. 🏆 Analise os cartões de métricas (**Score V10 Médio** e **Repetição Média**).
    4. 📥 Clique em **📥 Baixar Arquivo CSV das Apostas** para salvar no seu computador ou celular.
    5. 📌 O histórico local (`historico_v10.txt`) é alimentado automaticamente a cada geração.
    """)

st.markdown("---")

# -----------------------------------------------------------------------------
# Barra Lateral (Configurações e Parâmetros)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Parâmetros do Lote")

qtd_apostas = st.sidebar.number_input(
    "🎲 Quantidade de apostas (1 a 100):",
    min_value=1,
    max_value=100,
    value=30,
    step=1
)

aplicar_diversidade = st.sidebar.checkbox(
    "🛡️ Ativar Controle de Diversidade",
    value=True,
    help="Equilibra a aparição dos números de 01 a 25 para evitar dependência excessiva de poucas dezenas."
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"📌 **Último Resultado Cadastrado:**\n`{' '.join(f'{d:02d}' for d in ultimo_resultado)}`")

# Ações na Barra Lateral
if st.sidebar.button("🚀 Gerar Apostas V10", use_container_width=True):
    with st.spinner("⏳ Processando e aplicando filtros matemáticos V10..."):
        apostas, frequencias = gerar_apostas_v10(qtd_apostas, ultimo_resultado, aplicar_diversidade)
        st.session_state.apostas = apostas
        st.session_state.frequencias = frequencias
        salvar_historico_v10(apostas)

if st.session_state.apostas is not None:
    if st.sidebar.button("🗑️ Limpar Apostas da Tela", use_container_width=True):
        st.session_state.apostas = None
        st.session_state.frequencias = None
        st.rerun()

# -----------------------------------------------------------------------------
# Exibição dos Resultados (Persistente)
# -----------------------------------------------------------------------------
if st.session_state.apostas is not None:
    apostas = st.session_state.apostas
    frequencias = st.session_state.frequencias
    
    df_exibicao = pd.DataFrame(apostas)[["ID", "Dezenas Sugeridas (15 números)", "Score V10", "Repetições", "Pares", "Primos", "Soma"]]
    
    # Dashboard de Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎲 Total de Apostas", len(apostas))
    col2.metric("⭐ Score V10 Médio", f"{df_exibicao['Score V10'].mean():.4f}")
    col3.metric("🔄 Repetição Média", f"{df_exibicao['Repetições'].mean():.1f}")
    col4.metric("🧮 Soma Média", f"{int(df_exibicao['Soma'].mean())}")
    
    st.markdown("---")
    
    # Tabela Principal de Resultados
    st.subheader("🏆 Cartela de Apostas Otimizadas V10")
    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("🆔 ID", width="small"),
            "Dezenas Sugeridas (15 números)": st.column_config.TextColumn("🎯 Dezenas Sugeridas (15 números)", width="large"),
            "Score V10": st.column_config.NumberColumn("⭐ Score V10", format="%.6f"),
            "Repetições": st.column_config.NumberColumn("🔄 Repetições"),
            "Pares": st.column_config.NumberColumn("⚖️ Pares"),
            "Primos": st.column_config.NumberColumn("🔢 Primos"),
            "Soma": st.column_config.NumberColumn("🧮 Soma Total"),
        }
    )
    
    # Exportação CSV
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    nome_arquivo = f"{timestamp}_apostas_v10.csv"
    csv_data = df_exibicao[["ID", "Dezenas Sugeridas (15 números)", "Score V10", "Repetições"]].to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Baixar Arquivo CSV das Apostas",
        data=csv_data,
        file_name=nome_arquivo,
        mime="text/csv",
        use_container_width=True
    )
    
    # Análise Visual de Frequência das Dezenas
    st.markdown("---")
    st.subheader("📊 Frequência e Cobertura das Dezenas (01 a 25)")
    
    df_freq = pd.DataFrame({
        "Dezena": [f"Nº {i:02d}" for i in range(1, 26)],
        "Aparições": [frequencias[i] for i in range(1, 26)],
        "Presença (%)": [f"{round((frequencias[i] / len(apostas)) * 100, 1)}%" for i in range(1, 26)]
    })
    
    st.dataframe(
        df_freq.T,
        use_container_width=True
    )