import streamlit as st
import sqlite3
import pandas as pd
import random
import os

# Configuração da página
st.set_page_config(
    page_title="Lotofácil Pro V11", 
    page_icon="🎯", 
    layout="wide"
)

# ── CARREGAMENTO DE DADOS BLINDADO & DINÂMICO ─────────────────────────
@st.cache_data(ttl=300)
def carregar_dados_e_calcular():
    db_path = "database/lotofacil.db"
    
    if not os.path.exists(db_path):
        return None, f"Arquivo '{db_path}' não encontrado no repositório."

    try:
        conn = sqlite3.connect(db_path)
        
        # 1. Detecta as tabelas existentes no banco SQLite automaticamente
        tables_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", conn)
        table_names = tables_df['name'].tolist()
        
        if not table_names:
            conn.close()
            return None, "O banco SQLite está vazio (sem tabelas)."

        # Prioriza 'concursos' ou 'resultados', senão pega a primeira tabela que existir
        target_table = None
        for t in ['concursos', 'resultados', 'concursos_novo']:
            if t in table_names:
                target_table = t
                break
        if not target_table:
            target_table = table_names[0]

        df = pd.read_sql_query(f"SELECT * FROM {target_table}", conn)
        conn.close()
    except Exception as e:
        return None, f"Erro de conexão com o banco de dados: {e}"

    if df.empty:
        return None, f"A tabela '{target_table}' não possui registros."

    # 2. Localiza a coluna do número do concurso dinamicamente
    col_concurso = None
    for c in df.columns:
        if any(term in c.lower() for term in ['concurs', 'num', 'id']):
            col_concurso = c
            break

    if col_concurso:
        # Ordena pelo concurso
        df[col_concurso] = pd.to_numeric(df[col_concurso], errors='coerce')
        df = df.dropna(subset=[col_concurso]).sort_values(by=col_concurso, ascending=True).reset_index(drop=True)
        ultimo_concurso = int(df[col_concurso].iloc[-1])
    else:
        ultimo_concurso = len(df)

    concurso_alvo = ultimo_concurso + 1

    # 3. Extrai as 15 dezenas (1 a 25) de cada sorteio dinamicamente
    historico_sorteios = []
    numeric_cols = [c for c in df.columns if c != col_concurso]

    for _, row in df.iterrows():
        dezenas_jogo = set()
        for col in numeric_cols:
            val = row[col]
            if pd.notnull(val):
                try:
                    v_int = int(val)
                    if 1 <= v_int <= 25:
                        dezenas_jogo.add(v_int)
                except (ValueError, TypeError):
                    pass
        if len(dezenas_jogo) >= 15:
            historico_sorteios.append(sorted(list(dezenas_jogo))[:15])

    if not historico_sorteios:
        return None, "Não foi possível extrair as dezenas dos jogos na tabela."

    # 4. Análise do Ciclo (Dezenas Faltantes)
    todas_dezenas = set(range(1, 26))
    dezenas_sorteadas_ciclo = set()
    
    for jogo in reversed(historico_sorteios):
        dezenas_sorteadas_ciclo.update(jogo)
        if len(dezenas_sorteadas_ciclo) == 25:
            break

    faltantes_set = todas_dezenas - dezenas_sorteadas_ciclo
    if len(faltantes_set) == 0:
        faltantes_set = todas_dezenas

    faltantes = sorted(list(faltantes_set))
    qtd_faltantes = len(faltantes)

    # 5. Frequência das Últimas 30 Rodadas
    ultimos_30 = historico_sorteios[-30:]
    freq = {d: 0 for d in range(1, 26)}
    for jogo in ultimos_30:
        for d in jogo:
            freq[d] += 1

    # 6. Gerador Preditivo & Cálculo Score V10
    candidatos = []
    random.seed(concurso_alvo)

    for _ in range(500):
        num_faltantes_incluir = min(qtd_faltantes, random.choice([2, 3, 4]) if qtd_faltantes >= 3 else qtd_faltantes)
        escolhidas_faltantes = random.sample(faltantes, num_faltantes_incluir) if qtd_faltantes > 0 else []
        
        outras_opcoes = list(todas_dezenas - set(escolhidas_faltantes))
        resto = random.sample(outras_opcoes, 15 - len(escolhidas_faltantes))
        
        jogo_completo = sorted(escolhidas_faltantes + resto)
        
        score_base = sum(freq[d] for d in jogo_completo) / 15.0
        peso_ciclo = sum(1.25 for d in jogo_completo if d in faltantes) / max(1, qtd_faltantes)
        score_v10 = round(1.0 + (score_base / 30.0) * 0.1 + peso_ciclo * 0.05, 6)
        
        candidatos.append({
            "dezenas_lista": jogo_completo,
            "dezenas_str": " ".join([f"{d:02d}" for d in jogo_completo]),
            "score": score_v10,
            "rep": 9
        })

    candidatos = sorted(candidatos, key=lambda x: x['score'], reverse=True)
    jogos_unicos = []
    vistos = set()
    
    for c in candidatos:
        if c['dezenas_str'] not in vistos:
            vistos.add(c['dezenas_str'])
            jogos_unicos.append(c)
        if len(jogos_unicos) == 5:
            break

    for idx, j in enumerate(jogos_unicos, start=1):
        j['id'] = f"{idx:02d}"

    return {
        "ultimo_concurso": ultimo_concurso,
        "concurso_alvo": concurso_alvo,
        "faltantes": [f"{d:02d}" for d in faltantes],
        "qtd_faltantes": qtd_faltantes,
        "jogos": jogos_unicos
    }, None

# ── EXECUÇÃO E INTERFACE STREAMLIT ────────────────────────────────────
dados, erro = carregar_dados_e_calcular()

st.title("🎯 Lotofácil Pro V11")
st.caption("Sistema de Análise Preditiva & Inteligência Estatística")

col_head1, col_head2 = st.columns([3, 1])
with col_head2:
    modo_pro = st.toggle("⚙️ Modo Avançado / Pro", value=False)

st.divider()

if erro:
    st.error(f"⚠️ {erro}")
else:
    concurso_alvo = f"#{dados['concurso_alvo']}"
    ultimo_concurso = f"#{dados['ultimo_concurso']}"
    faltantes = dados['faltantes']
    qtd_faltantes = dados['qtd_faltantes']
    jogos = dados['jogos']

    if qtd_faltantes <= 4:
        status_texto = "🔥 FECHAMENTO DE CICLO PRÓXIMO"
        alerta_cor = st.success
    else:
        status_texto = "⏳ CICLO EM EMISSÃO (Aguardar maturação)"
        alerta_cor = st.info

    # ── MODO INICIANTE / LEIGO ────────────────────────────────────────
    if not modo_pro:
        st.info(f"📌 **Concurso Alvo:** {concurso_alvo} | **Último cadastrado:** {ultimo_concurso}")
        
        alerta_cor(f"**SITUAÇÃO DO CICLO:** {status_texto} (Faltam {qtd_faltantes} dezenas).")
        
        st.markdown("### 📋 Sugestões de Jogos para Hoje")
        st.caption("Escolha seus palpites e clique no código para copiar:")
        
        for jogo in jogos:
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"**Jogo #{jogo['id']}**")
                    st.code(jogo['dezenas_str'], language=None)
                with col_b:
                    st.caption("Score V10:")
                    st.write(f"**{jogo['score']:.4f}**")

    # ── MODO AVANÇADO / PRO ───────────────────────────────────────────
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Concurso Alvo", concurso_alvo)
        m2.metric("Status do Ciclo", status_texto)
        m3.metric("Faltantes no Ciclo", f"{qtd_faltantes} de 25")
        
        score_medio = sum(j['score'] for j in jogos) / len(jogos)
        m4.metric("Score Médio V10", f"{score_medio:.4f}")

        st.warning(f"**Dezenas Faltantes para Fechamento:** `{', '.join(faltantes)}`")
        
        st.markdown("### 📊 Tabela Preditiva Detalhada (Motor V11.2)")
        
        df_tabela = pd.DataFrame([
            {
                "ID": j['id'],
                "Dezenas Sugeridas (15 números)": j['dezenas_str'],
                "Score V10": j['score'],
                "Repetições": j['rep']
            } for j in jogos
        ])
        
        st.dataframe(
            df_tabela,
            column_config={
                "Score V10": st.column_config.NumberColumn(format="%.6f")
            },
            use_container_width=True,
            hide_index=True
        )
        
        st.caption("★ **Janela de Ouro:** Exige Faltantes ≤ 4 e Score V10 ≥ 1.18.")

st.divider()
st.caption("© 2026 Lotofácil Pro V11 — Todos os direitos reservados.")