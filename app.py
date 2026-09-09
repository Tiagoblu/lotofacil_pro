import streamlit as st
import os
import sys
import pandas as pd

# Configura diretório base para importação dos módulos do 'core'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configuração da página
st.set_page_config(
    page_title="Lotofácil Pro V11", 
    page_icon="🎯", 
    layout="wide"
)

# 🎨 DESIGN LIMPO
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ── CARREGAMENTO DE DADOS & MOTOR OFICIAL ─────────────────────────────
@st.cache_data(ttl=300)
def executar_motor_oficial():
    try:
        from core.infrastructure.downloader.baixar import baixar_dados_novos
        baixar_dados_novos()
    except Exception:
        pass

    try:
        from core.infrastructure.database.database import carregar_concursos
        from core.engine.probabilistic_engine import ProbabilisticEngine
    except ImportError as e:
        return None, f"Erro ao importar módulos do 'core': {e}"

    concursos = carregar_concursos()
    if not concursos:
        return None, "Base de dados vazia ou indisponível."

    ultimo = concursos[-1]
    alvo = ultimo.numero + 1

    engine = ProbabilisticEngine()
    jogos, info = engine.gerar_jogos(concursos)

    jogos_processados = []
    faltantes = info.get("dezenas_faltantes", [])
    novo_ciclo = info.get("novo_ciclo", False)

    for idx, (jogo_obj, score, rep) in enumerate(jogos, start=1):
        dezenas_ordenadas = sorted(list(jogo_obj.dezenas))
        dezenas_str = " ".join([f"{d:02d}" for d in dezenas_ordenadas])
        
        jogos_processados.append({
            "id": f"{idx:02d}",
            "dezenas_lista": dezenas_ordenadas,
            "dezenas_str": dezenas_str,
            "score": score,
            "rep": rep
        })

    return {
        "ultimo_concurso": ultimo.numero,
        "ultimo_data": ultimo.data,
        "concurso_alvo": alvo,
        "faltantes": [f"{d:02d}" for d in faltantes],
        "qtd_faltantes": len(faltantes),
        "novo_ciclo": novo_ciclo,
        "score_medio": info.get("score_medio", 0.0),
        "jogos": jogos_processados
    }, None

# ── EXECUÇÃO E INTERFACE STREAMLIT ────────────────────────────────────
dados, erro = executar_motor_oficial()

# Cabeçalho Principal e Botão de Ajuda
col_title, col_help = st.columns([3, 1])
with col_title:
    st.title("🎯 Lotofácil Pro V11")
    st.caption("Sistema de Análise Preditiva & Inteligência Estatística")

with col_help:
    st.write("") 
    with st.popover("ℹ️ Como Funciona, Etapas e Ciclos"):
        st.markdown("### 📘 Guia Completo: Etapas, Ciclos & Janela de Ouro")
        st.markdown("""
        O **Lotofácil Pro V11** opera identificando a maturidade dos ciclos e a força estatística das dezenas.

        ---
        #### 🔄 As 3 Etapas do Ciclo
        * **🟢 Etapa 1: Início do Ciclo (Faltam 10 a 25 dezenas)** — Observação e reajuste inicial.
        * **🟡 Etapa 2: Maturação (Faltam 5 a 9 dezenas)** — Afunilamento das dezenas quentes.
        * **🔴 Etapa 3: Fechamento do Ciclo (Faltam 1 a 4 dezenas)** — Reta final com alta probabilidade de fechamento.

        ---
        #### ⭐ A JANELA DE OURO (A MELHOR CHANCE / APOSTA MÁXIMA!)
        * **🎯 Requisitos:** Ciclo na **Etapa 3** (Faltando **≤ 4 dezenas**) e **Score V10 ≥ 1.1800**.
        * **🔥 Por que apostar?** Ponto de máxima convergência probabilística entre dezenas faltantes e dezenas quentes.
        """)

st.divider()

if erro:
    st.error(f"⚠️ {erro}")
else:
    concurso_alvo = f"#{dados['concurso_alvo']}"
    ultimo_concurso = f"#{dados['ultimo_concurso']} ({dados['ultimo_data']})"
    faltantes = dados['faltantes']
    qtd_faltantes = dados['qtd_faltantes']
    todos_jogos = dados['jogos']
    novo_ciclo = dados['novo_ciclo']

    # Controles
    c_ctrl1, c_ctrl2 = st.columns([3, 1])
    with c_ctrl1:
        qtd_gerar = st.slider(
            "🎲 Quantidade de Jogos Desejada:", 
            min_value=5, 
            max_value=30, 
            value=5, 
            step=5
        )
    with c_ctrl2:
        st.write("")
        modo_pro = st.toggle("⚙️ Modo Avançado / Pro", value=False)

    jogos_filtrados = todos_jogos[:qtd_gerar]

    # Score médio real dos jogos selecionados na tela
    score_medio_sel = sum(j['score'] for j in jogos_filtrados) / len(jogos_filtrados) if jogos_filtrados else 0.0

    # Texto padronizado de dezenas faltantes
    if qtd_faltantes == 1:
        txt_dezenas = f"Falta 1 dezena para fechamento: **{faltantes[0]}**"
    elif qtd_faltantes > 1:
        txt_dezenas = f"Faltam {qtd_faltantes} dezenas para fechamento: **{', '.join(faltantes)}**"
    else:
        txt_dezenas = "Nenhuma dezena faltante (Ciclo Fechado)"

    # Lógica de Status & Janela de Ouro (Melhor Chance)
    janela_ouro_ativa = (qtd_faltantes <= 4 and score_medio_sel >= 1.18)

    if novo_ciclo or qtd_faltantes == 0:
        status_titulo = "INÍCIO DE NOVO CICLO"
        emoji_sinal = "🔴"
        alerta_func = st.error
    elif janela_ouro_ativa:
        status_titulo = "JANELA DE OURO ATIVA — MELHOR CHANCE (APOSTA MÁXIMA)"
        emoji_sinal = "🟢"
        alerta_func = st.success
    elif qtd_faltantes <= 4:
        status_titulo = "FECHAMENTO DE CICLO PRÓXIMO"
        emoji_sinal = "🟡"
        alerta_func = st.warning
    else:
        status_titulo = "OPORTUNIDADE ESTATÍSTICA ATIVA"
        emoji_sinal = "🟢"
        alerta_func = st.info

    # Texto explicativo da Janela de Ouro
    if janela_ouro_ativa:
        txt_janela_ouro = "⭐ **MELHOR CHANCE CONFIRMADA (⭐ Janela de Ouro):** Ciclo na reta final (≤ 4 dezenas) e Score Médio ≥ 1.1800. Ponto ideal para aposta!"
    else:
        txt_janela_ouro = f"ℹ️ **Condição para a MELHOR CHANCE (⭐ Janela de Ouro):** Exige Faltantes ≤ 4 e Score V10 ≥ 1.1800 *(Score Atual dos Jogos: {score_medio_sel:.4f})*."

    # ── PAINEL / INFORMATIVO DE EMOJIS (GUIA DE STATUS E OPORTUNIDADE) ──
    with st.expander("🔥 JANELA ESPECIAL: Sinalizador de Oportunidade e Guia de Emojis 💰", expanded=True):
        st.markdown(f"### 📊 Status Atual: {emoji_sinal} **{status_titulo}**")
        st.markdown(f"* **Situação das Dezenas:** {txt_dezenas}")
        st.markdown(f"* **Score V10 Médio Atual:** `{score_medio_sel:.4f}`")
        st.markdown(f"* **Diagnóstico de Aposta:** {txt_janela_ouro}")
        
        st.markdown("""
        ---
        ### 🚦 Guia dos Sinalizadores de Oportunidade:
        
        * 🟢 **SINAL VERDE (Excelente Oportunidade / ⭐ Janela de Ouro):** Faltam **≤ 4 dezenas** no ciclo e o Score V10 Médio é **≥ 1.1800**. Alta convergência estatística.
        * 🟡 **SINAL AMARELO (Oportunidade Moderada):** Faltam **≤ 4 dezenas**, mas o Score V10 Médio está abaixo de 1.1800.
        * 🔴 **SINAL VERMELHO (Atenção / Risco Elevado):** Início de novo ciclo ou muitas dezenas faltantes (5 a 25 dezenas).
        """)

    # ── MODO PADRÃO / INICIANTE ───────────────────────────────────────
    if not modo_pro:
        st.info(f"📌 **Concurso Alvo:** {concurso_alvo} | **Último cadastrado:** {ultimo_concurso}")
        
        st.markdown(f"### 📋 Sugestões de {qtd_gerar} Jogos para Hoje")
        st.caption("Escolha seus palpites e clique no código para copiar:")
        
        for jogo in jogos_filtrados:
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"**Jogo #{jogo['id']}**")
                    st.code(jogo['dezenas_str'], language=None)
                with col_b:
                    st.caption("Score V10:")
                    st.write(f"**{jogo['score']:.6f}**")

    # ── MODO AVANÇADO / PRO ───────────────────────────────────────────
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Concurso Alvo", concurso_alvo, help="Próximo concurso a ser sorteado")
        m2.metric("Faltantes no Ciclo", f"{qtd_faltantes} de 25", help="Quantidade de dezenas restantes no ciclo")
        m3.metric("Score Médio dos Selecionados", f"{score_medio_sel:.6f}", help="Média do Score V10 dos bilhetes exibidos (Meta para ⭐ Janela de Ouro: ≥ 1.1800)")

        st.markdown(f"### 📊 Tabela Preditiva Detalhada ({qtd_gerar} Jogos)")
        
        df_tabela = pd.DataFrame([
            {
                "ID": j['id'],
                "Dezenas Sugeridas (15 números)": j['dezenas_str'],
                "Score V10": j['score'],
                "Repetições": j['rep']
            } for j in jogos_filtrados
        ])
        
        st.dataframe(
            df_tabela,
            column_config={
                "Score V10": st.column_config.NumberColumn(format="%.6f")
            },
            use_container_width=True,
            hide_index=True
        )
        
        if janela_ouro_ativa:
            st.success("⭐ **Janela de Ouro Ativa:** Todos os critérios de máxima probabilidade foram atingidos.")
        else:
            st.caption(f"⭐ **Janela de Ouro (Melhor Chance):** Requer Faltantes ≤ 4 e Score V10 ≥ 1.1800 (Score atual: **{score_medio_sel:.6f}**).")

st.divider()
st.caption("© 2026 Lotofácil Pro V11 — Todos os direitos reservados.")