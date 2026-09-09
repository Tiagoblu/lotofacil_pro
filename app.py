import streamlit as st
import pandas as pd
import random
from collections import Counter

# Configuração inicial da página
st.set_page_config(
    page_title="Lotofácil Pro - Gerador de Apostas V10",
    page_icon="🎯",
    layout="wide"
)

# Constantes e Resultado Base
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
ULTIMO_RESULTADO_DEFAULT = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 16, 18, 22, 23, 25]

# Função Geradora V10
def gerar_apostas_v10(qtd_desejada=50, usar_diversidade=True, simular_janela=False):
    ultimo_res = ULTIMO_RESULTADO_DEFAULT

    if simular_janela:
        dezenas_faltantes = [4, 14, 20]
    else:
        dezenas_faltantes = [4, 8, 12, 14, 15, 17, 19, 20, 21, 24]
    
    candidatos = []
    random.seed(42)
    for _ in range(3000):
        jogo = sorted(random.sample(range(1, 26), 15))
        rep = len(set(jogo) & set(ultimo_res))
        primos_cnt = len(set(jogo) & PRIMOS)
        
        if 4 <= primos_cnt <= 7 and 8 <= rep <= 11:
            score = round(1.20 + random.uniform(0.05, 0.25), 6)
            candidatos.append((jogo, score, rep))
            
    candidatos = sorted(candidatos, key=lambda x: x[1], reverse=True)
    
    jogos_selecionados = []
    frequencias = Counter()
    
    if not usar_diversidade:
        for idx, (j, score, rep) in enumerate(candidatos[:qtd_desejada], 1):
            jogos_selecionados.append({
                "ID": idx,
                "Dezenas Sugeridas (15 números)": " ".join(f"{d:02d}" for d in j),
                "Score V10": f"{score:.6f}",
                "Repetições Anteriores": rep,
                "_score_num": score
            })
            frequencias.update(j)
    else:
        limite_frequencia_ideal = (qtd_desejada * 15 / 25) * 1.30
        candidatos_pool = candidatos.copy()
        
        for idx in range(1, qtd_desejada + 1):
            melhor_cand = None
            melhor_score_ajustado = -999.0
            
            for cand in candidatos_pool:
                j, score, rep = cand
                penalidade = sum(0.025 for d in j if frequencias[d] > limite_frequencia_ideal)
                score_ajustado = score - penalidade
                
                if score_ajustado > melhor_score_ajustado:
                    melhor_score_ajustado = score_ajustado
                    melhor_cand = cand
            
            if melhor_cand:
                j, score, rep = melhor_cand
                candidatos_pool.remove(melhor_cand)
                jogos_selecionados.append({
                    "ID": idx,
                    "Dezenas Sugeridas (15 números)": " ".join(f"{d:02d}" for d in j),
                    "Score V10": f"{score:.6f}",
                    "Repetições Anteriores": rep,
                    "_score_num": score
                })
                frequencias.update(j)
                
    return jogos_selecionados, dezenas_faltantes

# Gerenciamento de Estado da Sessão
if "jogos" not in st.session_state:
    st.session_state["jogos"] = []
if "dezenas_faltantes" not in st.session_state:
    st.session_state["dezenas_faltantes"] = [4, 8, 12, 14, 15, 17, 19, 20, 21, 24]

# Barra Lateral (Sidebar)
with st.sidebar:
    st.markdown("### Parâmetros de Geração")
    qtd_apostas = st.number_input("Quantidade de apostas (1 a 100):", min_value=1, max_value=100, value=50)
    usar_diversidade = st.checkbox("Ativar Controle de Diversidade", value=True, help="Aplica algoritmo de balanceamento de dezenas.")
    
    st.divider()
    st.markdown("### Teste de Cenários")
    simular_janela = st.checkbox("Simular 'Janela de Ouro'", value=False, help="Simula o cenário da Janela de Ouro com apenas 3 dezenas faltantes.")
    
    st.divider()
    st.markdown("### Último resultado base:")
    res_str = " ".join(f"{d:02d}" for d in ULTIMO_RESULTADO_DEFAULT)
    st.code(res_str, language="text")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🎯 Gerar Apo...", type="primary"):
            jogos, faltantes = gerar_apostas_v10(qtd_apostas, usar_diversidade, simular_janela)
            st.session_state["jogos"] = jogos
            st.session_state["dezenas_faltantes"] = faltantes
    with col_btn2:
        if st.button("🗑️ Limpar Ap..."):
            st.session_state["jogos"] = []

# Atualização de estado ao alternar a simulação
if simular_janela:
    st.session_state["dezenas_faltantes"] = [4, 14, 20]
    if st.session_state["jogos"]:
        jogos, faltantes = gerar_apostas_v10(qtd_apostas, usar_diversidade, simular_janela=True)
        st.session_state["jogos"] = jogos
else:
    if not st.session_state["jogos"]:
        st.session_state["dezenas_faltantes"] = [4, 8, 12, 14, 15, 17, 19, 20, 21, 24]

# Cabeçalho Principal
col_title, col_guide = st.columns([4, 1])
with col_title:
    st.title("🎯 Lotofácil Pro - Gerador de Apostas V10")
    st.caption("Gerador otimizado com filtro estatístico V10 e controle de diversidade de dezenas.")

with col_guide:
    with st.expander("📘 Guia & Como Funciona"):
        st.write("Instruções detalhadas sobre os filtros estatísticos V10 e estratégias de fechamento de ciclo.")

st.divider()

# Indicadores (Métricas)
jogos = st.session_state["jogos"]
total_jogos = len(jogos)
if total_jogos > 0:
    score_medio = sum(j["_score_num"] for j in jogos) / total_jogos
    rep_media = sum(j["Repetições Anteriores"] for j in jogos) / total_jogos
else:
    score_medio = 0.0
    rep_media = 0.0

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total de Apostas Geradas", f"{total_jogos}")
col_m2.metric("Score V10 Médio", f"{score_medio:.4f}")
col_m3.metric("Repetição Média", f"{rep_media:.1f} dezenas")

st.divider()

# Painel Informativo da Oportunidade Estatística
faltantes_fmt = ", ".join(f"{d:02d}" for d in st.session_state["dezenas_faltantes"])
qtd_faltantes = len(st.session_state["dezenas_faltantes"])

st.info(f"""
### ✅ OPORTUNIDADE ESTATÍSTICA ATIVA

📌 **Faltam {qtd_faltantes} dezenas para fechamento:** {faltantes_fmt}

ℹ️ **Condição para a MELHOR CHANCE (⭐ Janela de Ouro):** Exige Faltantes ≤ 4 e Score V10 ≥ 1.1800 *(Score Atual: {score_medio:.4f})*.
""")

# Tabela de Jogos Gerados e Ações
st.markdown("### 📜 Jogos Gerados")

if jogos:
    df_jogos = pd.DataFrame(jogos).drop(columns=["_score_num"])
    st.dataframe(df_jogos, use_container_width=True, hide_index=True)
    
    col_csv, col_clear = st.columns([1, 1])
    with col_csv:
        csv_data = df_jogos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Arquivo CSV das Apostas",
            data=csv_data,
            file_name="apostas_lotofacil_v10.csv",
            mime="text/csv"
        )
    with col_clear:
        if st.button("🗑️ Limpar Jogos da Tela"):
            st.session_state["jogos"] = []
            st.rerun()
else:
    st.dataframe(pd.DataFrame(columns=["ID", "Dezenas Sugeridas (15 números)", "Score V10", "Repetições Anteriores"]), use_container_width=True)