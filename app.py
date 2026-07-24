import streamlit as st
import sqlite3
import os

# Configuração da página
st.set_page_config(
    page_title="Lotofácil Pro V11", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CABEÇALHO PRINCIPAL ───────────────────────────────────────────────
st.title("🎯 Lotofácil Pro V11")
st.caption("Sistema de Análise Preditiva & Inteligência Estatística")

# ── CONTROLE DE PERFIL (Progressive Disclosure) ───────────────────────
col_head1, col_head2 = st.columns([3, 1])
with col_head2:
    modo_pro = st.toggle("⚙️ Modo Avançado / Pro", value=False)

st.divider()

# ── DADOS DO CONCURSO ATUAL (#3744) ──────────────────────────────────
concurso_alvo = "#3744"
ultimo_concurso = "#3743 (23/07/2026)"
faltantes = ["07", "08", "17", "24"]
qtd_faltantes = len(faltantes)

# Jogos simulados com a inteligência do seu algoritmo
jogos = [
    {
        "id": "01",
        "dezenas": "02 05 07 08 09 12 15 16 17 18 19 21 22 23 25",
        "score": 1.105753,
        "rep": 9
    },
    {
        "id": "02",
        "dezenas": "03 04 07 08 09 11 13 16 17 18 19 22 23 24 25",
        "score": 1.103796,
        "rep": 9
    },
    {
        "id": "03",
        "dezenas": "02 03 06 07 08 11 15 16 17 19 20 21 23 24 25",
        "score": 1.087596,
        "rep": 9
    },
    {
        "id": "04",
        "dezenas": "02 05 06 07 08 11 15 16 17 18 20 21 22 23 25",
        "score": 1.084881,
        "rep": 9
    },
    {
        "id": "05",
        "dezenas": "03 05 07 08 09 10 11 16 17 18 20 21 22 24 25",
        "score": 1.048664,
        "rep": 9
    }
]

# ── VISÃO DO USUARIO LEIGO / INICIANTE (MODO PADRÃO) ──────────────────
if not modo_pro:
    st.info(f"📌 **Concurso Alvo:** {concurso_alvo} | **Último cadastrado:** {ultimo_concurso}")
    
    # Card de status simples
    st.success("🔥 **SITUAÇÃO DO CICLO:** O ciclo está muito próximo de fechar! Boa oportunidade de aposta.")
    
    st.markdown("### 📋 Sugestões de Jogos para Hoje")
    st.caption("Escolha um ou mais jogos abaixo e clique no código para copiar facilmente:")
    
    for jogo in jogos:
        with st.container(border=True):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.markdown(f"**Jogo #{jogo['id']}**")
                # Código formatado - o usuário clica e copia no celular/PC
                st.code(jogo['dezenas'], language=None)
            with col_b:
                st.caption("Foco do Jogo:")
                st.write("Equilibrado")

# ── VISÃO DO USUÁRIO AVANÇADO (MODO PRO) ──────────────────────────────
else:
    # Painel de Métricas Avançadas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Concurso Alvo", concurso_alvo)
    m2.metric("Status do Ciclo", "🔥 Fechamento Próximo")
    m3.metric("Faltantes no Ciclo", f"{qtd_faltantes} de 25")
    m4.metric("Score Médio V10", "1.0861", delta="+0.03")

    st.warning(f"**Dezenas Faltantes para Fechamento:** `{', '.join(faltantes)}`")
    
    st.markdown("### 📊 Tabela Preditiva Detalhada (Motor V11.2)")
    
    # Tabela com as métricas completas
    st.dataframe(
        jogos,
        column_config={
            "id": "ID",
            "dezenas": "Dezenas Sugeridas (15 números)",
            "score": st.column_config.NumberColumn("Score V10", format="%.6f"),
            "rep": "Repetições"
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.caption("★ **Janela de Ouro:** Exige Faltantes ≤ 4 e Score V10 ≥ 1.18.")

# ── RODAPÉ ───────────────────────────────────────────────────────────
st.divider()
st.caption("© 2026 Lotofácil Pro V11 — Todos os direitos reservados.")