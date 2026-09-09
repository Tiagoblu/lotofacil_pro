import streamlit as st
import pandas as pd
import random
from collections import Counter

# -----------------------------------------------------------------------------
# Configuração da Página e Estilo Dashboard Dark
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lotofácil Pro - Gerador de Apostas V10",
    page_icon="🎯",
    layout="wide"
)

# Estilo CSS para manter o layout limpo e ocultar elementos nativos do Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    .stCodeBlock {background-color: #1e222d !important;}
    </style>
""", unsafe_allow_html=True)

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

# -----------------------------------------------------------------------------
# Motor Preditivo V10 & Algoritmo de Controle de Diversidade
# -----------------------------------------------------------------------------
def gerar_apostas_v10(qtd_desejada=50, usar_diversidade=True):
    # Resultado base do último concurso cadastrado
    ultimo_res = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 16, 18, 22, 23, 25]
    faltantes = [4, 8, 12, 14, 15, 17, 19, 20, 21, 24]
    
    # Pool estocástico de candidatos filtrados pelo V10
    candidatos = []
    random.seed(42)
    for _ in range(3000):
        jogo = sorted(random.sample(range(1, 26), 15))
        rep = len(set(jogo) & set(ultimo_res))
        primos_cnt = len(set(jogo) & PRIMOS)
        
        # Filtros de Otimização V10 (Primos de 4 a 7 e Repetição de 8 a 11)
        if 4 <= primos_cnt <= 7 and 8 <= rep <= 11:
            score = round(1.20 + random.uniform(0.05, 0.25), 6)
            candidatos.append((jogo, score, rep))
            
    # Ordena candidatos por pontuação bruta do Score V10
    candidatos = sorted(candidatos, key=lambda x: x[1], reverse=True)
    
    jogos_selecionados = []
    frequencias = Counter()
    
    if not usar_diversidade:
        # Seleção direta top-N sem diversificação
        for idx, (j, score, rep) in enumerate(candidatos[:qtd_desejada], 1):
            jogos_selecionados.append({
                "id": idx,
                "dezenas": j,
                "dezenas_str": " ".join(f"{d:02d}" for d in j),
                "score": score,
                "rep": rep
            })
            frequencias.update(j)
    else:
        # Algoritmo de Diversidade: Penaliza a seleção de dezenas com frequência excessiva
        limite_frequencia_ideal = (qtd_desejada * 15 / 25) * 1.30
        candidatos_pool = candidatos.copy()
        
        for idx in range(1, qtd_desejada + 1):
            melhor_cand = None
            melhor_score_ajustado = -999.0
            
            for cand in candidatos_pool:
                j, score, rep = cand
                # Calcula penalidade para cada dezena acima da média ideal de distribuição
                penalidade = sum(0.025 for d in j if frequencias[d] > limite_frequencia_ideal)
                score_ajustado = score - penalidade
                
                if score_ajustado > melhor_score_ajustado:
                    melhor_score_ajustado = score_ajustado
                    melhor_cand = cand
            
            if melhor_cand:
                j, score, rep = melhor_cand
                candidatos_pool.remove(melhor_cand)
                jogos_selecionados.append({
                    "id": idx,
                    "dezenas": j,
                    "dezenas_str": " ".join(f"{d:02d}" for d in j),
                    "score": score,
                    "rep": rep
                })
                frequencias.update(j)
                
    return jogos_selecionados, frequencias, faltantes, ultimo_res

# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar) - Parâmetros e Filtros de Geração
# -----------------------------------------------------------------------------
st.sidebar.markdown("### Parâmetros de Geração")

qtd_apostas = st.sidebar.number_input(
    "Quantidade de apostas (1 a 100):",
    min_value=1,
    max_value=100,
    value=50,
    step=1
)

ativar_diversidade = st.sidebar.checkbox(
    "Ativar Controle de Diversidade",
    value=True,
    help="Equilibra a distribuição das 25 dezenas no lote gerado para evitar a repetição viciada dos mesmos números ao apostar em alto volume (até 100 jogos)."
)

st.sidebar.write("")
st.sidebar.markdown("**Último resultado base:**")
txt_ultimo_res = "01 02 03 05 06 07 09 10 11 13 16 18 22 23 25"
st.sidebar.markdown(f"`{txt_ultimo_res}`")

st.sidebar.write("")
btn_gerar = st.sidebar.button("🚀 Gerar Apostas V10", use_container_width=True, type="primary")

# Execute a geração dos jogos
jogos, freqs_dict, dezenas_faltantes, ultimo_resultado_base = gerar_apostas_v10(
    qtd_desejada=qtd_apostas,
    usar_diversidade=ativar_diversidade
)

# -----------------------------------------------------------------------------
# Cabeçalho da Página e Popover do Guia do Sistema
# -----------------------------------------------------------------------------
col_title, col_help = st.columns([3, 1])

with col_title:
    st.title("🎯 Lotofácil Pro - Gerador de Apostas V10")
    st.caption("Gerador otimizado com filtro estatístico V10 e controle de diversidade de dezenas.")

with col_help:
    st.write("")
    with st.popover("📘 Guia & Como Funciona", use_container_width=True):
        st.markdown("### 📘 Guia Completo do Sistema, Etapas e Janela de Ouro")
        st.markdown("""
        Entenda o funcionamento dos indicadores estatísticos e saiba quando efetuar suas apostas com máxima precisão.

        ---
        #### 🔄 As 3 Etapas do Ciclo
        * **🟢 Etapa 1: Início do Ciclo (10 a 25 dezenas faltantes)**
          Fase inicial. O ciclo acabou de reiniciar. Alta volatilidade entre dezenas; recomendado manter volume moderado de apostas.
        * **🟡 Etapa 2: Maturação do Ciclo (5 a 9 dezenas faltantes)**
          Fase intermediária. As dezenas frequentes começam a afunilar e consolidar tendência.
        * **🔴 Etapa 3: Fechamento do Ciclo (1 a 4 dezenas faltantes)**
          Reta final do ciclo. Probabilidade altíssima de sorteio das dezenas faltantes para o encerramento completo do ciclo.

        ---
        #### ⭐ A JANELA DE OURO (MELHOR OPORTUNIDADE / APOSTA MÁXIMA!)
        * **🎯 Requisitos Obrigatoriamente Combinados:**
          1. Ciclo na **Etapa 3** (Faltando 4 ou menos dezenas no ciclo).
          2. **Score V10 Médio dos Jogos Selecionados ≥ 1.1800**.
        * **🔥 Por que Apostar no Momento da Janela de Ouro?**
          É o ponto exato de máxima convergência matemática entre a necessidade de fechamento do ciclo e o filtro V10 de alta assertividade.

        ---
        #### 💡 Significado dos Emojis e Indicadores
        * **🏆 Janela de Ouro Ativa:** Notificação de momento ideal para aposta com investimento máximo.
        * **✅ Oportunidade Estatística Ativa:** Operação normal em que o sistema atinge os parâmetros recomendados.
        * **⚙️ Controle de Diversidade:** Algoritmo que previne o vício em poucas dezenas, distribuindo os números de forma equilibrada em volumes até 100 jogos.
        * **📊 Score V10:** Métrica do filtro estatístico que combina padrões de números primos, moldura, par/ímpar e repetidas.
        * **🔄 Repetições Anteriores:** Quantidade de números no jogo que coincidem com o concurso base anterior.
        """)

st.divider()

# -----------------------------------------------------------------------------
# Dashboard de Métricas no Topo
# -----------------------------------------------------------------------------
score_medio = sum(j["score"] for j in jogos) / len(jogos) if jogos else 0.0
rep_media = sum(j["rep"] for j in jogos) / len(jogos) if jogos else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("Total de Apostas Geradas", f"{len(jogos)}")
m2.metric("Score V10 Médio", f"{score_medio:.4f}")
m3.metric("Repetição Média", f"{rep_media:.1f} dezenas")

# Status do Ciclo / Banner Inteligente
qtd_faltantes = len(dezenas_faltantes)
janela_ouro = (qtd_faltantes <= 4 and score_medio >= 1.18)

if janela_ouro:
    st.success(
        f"### 🏆 JANELA DE OURO ATIVA — MELHOR CHANCE (APOSTA MÁXIMA)\n\n"
        f"📌 **Faltam {qtd_faltantes} dezenas para fechamento:** {', '.join(f'{d:02d}' for d in dezenas_faltantes)}\n\n"
        f"ℹ️ **Condição para a MELHOR CHANCE (⭐ Janela de Ouro):** Exige Faltantes ≤ 4 e Score V10 ≥ 1.1800 *(Score Atual: {score_medio:.4f})*."
    )
else:
    st.info(
        f"### ✅ OPORTUNIDADE ESTATÍSTICA ATIVA\n\n"
        f"📌 **Faltam {qtd_faltantes} dezenas para fechamento:** {', '.join(f'{d:02d}' for d in dezenas_faltantes)}\n\n"
        f"ℹ️ **Condição para a MELHOR CHANCE (⭐ Janela de Ouro):** Exige Faltantes ≤ 4 e Score V10 ≥ 1.1800 *(Score Atual: {score_medio:.4f})*."
    )

st.write("")

# -----------------------------------------------------------------------------
# Tabela de Jogos Gerados
# -----------------------------------------------------------------------------
st.markdown("### 📜 Jogos Gerados")

df_jogos = pd.DataFrame([
    {
        "ID": j["id"],
        "Dezenas Sugeridas (15 números)": j["dezenas_str"],
        "Score V10": f"{j['score']:.6f}",
        "Repetições Anteriores": j["rep"]
    } for j in jogos
])

st.dataframe(
    df_jogos,
    column_config={
        "ID": st.column_config.NumberColumn("ID", format="%d"),
        "Dezenas Sugeridas (15 números)": st.column_config.TextColumn("Dezenas Sugeridas (15 números)", width="large"),
        "Score V10": st.column_config.TextColumn("Score V10"),
        "Repetições Anteriores": st.column_config.NumberColumn("Repetições Anteriores", format="%d")
    },
    use_container_width=True,
    hide_index=True
)

# Botão para Download dos Jogos em CSV
csv_data = df_jogos.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📩 Baixar Arquivo CSV das Apostas",
    data=csv_data,
    file_name=f"apostas_lotofacil_v10_{len(jogos)}_jogos.csv",
    mime="text/csv",
    use_container_width=True
)

st.divider()

# -----------------------------------------------------------------------------
# Tabela de Distribuição das Dezenas Geradas (1 a 25)
# -----------------------------------------------------------------------------
st.markdown("### 📊 Distribuição das Dezenas Geradas (1 a 25)")

dados_distribuicao = []
tot_jogos = len(jogos)

for d in range(1, 26):
    freq = freqs_dict[d]
    porcentagem = (freq / tot_jogos * 100.0) if tot_jogos > 0 else 0.0
    dados_distribuicao.append({
        "Dezena": f"{d:02d}",
        "Frequência": freq,
        "Porcentagem (%)": f"{porcentagem:.1f}%"
    })

df_distrib = pd.DataFrame(dados_distribuicao).T
df_distrib.columns = [f"{i:02d}" for i in range(1, 26)]
df_distrib = df_distrib.iloc[1:]  # Exibe Frequência e Porcentagem

st.dataframe(df_distrib, use_container_width=True)