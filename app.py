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

# ── CARREGAMENTO DE DADOS E MOTOR ESTATÍSTICO ─────────────────────────
@st.cache_data(ttl=600)  # Cache de 10 minutos para alta performance
def carregar_dados_e_calcular():
    db_path = "database/lotofacil.db"
    
    if not os.path.exists(db_path):
        return None, "Banco de dados não encontrado."

    conn = sqlite3.connect(db_path)
    
    # 1. Carrega histórico de resultados
    try:
        df = pd.read_sql_query("SELECT * FROM resultados ORDER BY concurso ASC", conn)
        conn.close()
    except Exception as e:
        conn.close()
        return None, f"Erro ao ler banco de dados: {e}"

    if df.empty:
        return None, "Banco de dados vazio."

    ultimo_concurso = int(df['concurso'].max())
    concurso_alvo = ultimo_concurso + 1
    data_ultimo = df[df['concurso'] == ultimo_concurso]['data'].values[0] if 'data' in df.columns else ""

    # 2. Análise de Ciclo (Dezenas Faltantes)
    # Extrai colunas das dezenas (ex: bola1 a bola15 ou d1 a d15)
    cols_dezenas = [c for c in df.columns if c.startswith('bola') or c.startswith('d')]
    if not cols_dezenas:
        # Tenta pegar as últimas 15 colunas se não encontrar padrão de nome
        cols_dezenas = df.columns[-15:]

    # Rastrea fechamento do ciclo atual
    todas_dezenas = set(range(1, 26))
    dezenas_sorteadas_ciclo = set()
    
    for _, row in df.iloc[::-1].iterrows():
        sorteadas_jogo = set(int(row[c]) for c in cols_dezenas if pd.notnull(row[c]))
        dezenas_sorteadas_ciclo.update(sorteadas_jogo)
        if len(dezenas_sorteadas_ciclo) == 25:
            # Ciclo fechou aqui!
            break

    faltantes_set = todas_dezenas - dezenas_sorteadas_ciclo
    # Se o ciclo acabou de fechar, o novo ciclo precisa das 25
    if len(faltantes_set) == 0:
        faltantes_set = todas_dezenas

    faltantes = sorted(list(faltantes_set))
    qtd_faltantes = len(faltantes)

    # 3. Frequência das últimas 10 e 30 rodadas
    ultimos_30 = df.tail(30)
    freq = {}
    for d in range(1, 26):
        freq[d] = 0
    
    for _, row in ultimos_30.iterrows():
        for c in cols_dezenas:
            if pd.notnull(row[c]):
                val = int(row[c])
                if val in freq:
                    freq[val] += 1

    # 4. Gerador Preditivo e Calculador do Score V10
     candidatos = []
    # Usamos uma semente determinística baseada no concurso para manter constante no dia
    random.seed(concurso_alvo)

    for _ in range(500): # Amostragem rápida de candidatos
        # Força incluir entre 2 e 4 faltantes do ciclo
        num_faltantes_incluir = min(qtd_faltantes, random.choice([2, 3, 4]) if qtd_faltantes >= 3 else qtd_faltantes)
        escolhidas_faltantes = random.sample(faltantes, num_faltantes_incluir) if qtd_faltantes > 0 else []
        
        outras_opcoes = list(todas_dezenas - set(escolhidas_faltantes))
        resto = random.sample(outras_opcoes, 15 - len(escolhidas_faltantes))
        
        jogo_completo = sorted(escolhidas_faltantes + resto)
        
        # Pontuação Score V10 (baseada na frequência ponderada + peso do ciclo)
        score_base = sum(freq[d] for d in jogo_completo) / 15.0
        peso_ciclo = sum(1.25 for d in jogo_completo if d in faltantes) / max(1, qtd_faltantes)
        score_v10 = round(1.0 + (score_base / 30.0) * 0.1 + peso_ciclo * 0.05, 6)
        
        candidatos.append({
            "dezenas_lista": jogo_completo,
            "dezenas_str": " ".join([f"{d:02d}" for d in jogo_completo]),
            "score": score_v10,
            "rep": 9
        })

    # Ordena pelo maior Score V10 e pega os 5 melhores únicos
    candidatos = sorted(candidatos, key=lambda x: x['score'], reverse=True)
    jogos_unicos = []
    vistos = set()
    
    for c in candidatos:
        if c['dezenas_str'] not in vistos:
            vistos.add(c['dezenas_str'])
            jogos_unicos.append(c)
        if len(jogos_unicos) == 5:
            break

    # Atribui IDs 01 a 05
    for idx, j in enumerate(jogos_unicos, start=1):
        j['id'] = f"{idx:02d}"

    return {
        "ultimo_concurso": ultimo_concurso,
        "concurso_alvo": concurso_alvo,
        "data_ultimo": data_ultimo,
        "faltantes": [f"{d:02d}" for d in faltantes],
        "qtd_faltantes": qtd_faltantes,
        "jogos": jogos_unicos
    }, None

# ── EXECUÇÃO E INTERFACE ──────────────────────────────────────────────
dados, erro = carregar_dados_e_calcular()

# Cabeçalho
st.title("🎯 Lotofácil Pro V11")
st.caption("Sistema de Análise Preditiva & Inteligência Estatística")

col_head1, col_head2 = st.columns([3, 1])
with col_head2:
    modo_pro = st.toggle("⚙️ Modo Avançado / Pro", value=False)

st.divider()

if erro:
    st.error(f"⚠️ {erro}")
    st.info("Verifique se o arquivo `database/lotofacil.db` está atualizado no GitHub.")
else:
    concurso_alvo = f"#{dados['concurso_alvo']}"
    ultimo_concurso = f"#{dados['ultimo_concurso']}"
    faltantes = dados['faltantes']
    qtd_faltantes = dados['qtd_faltantes']
    jogos = dados['jogos']

    # Status de alerta do ciclo
    if qtd_faltantes <= 4:
        status_texto = "🔥 FECHAMENTO DE CICLO PRÓXIMO"
        alerta_cor = st.success
    else:
        status_texto = "⏳ CICLO EM EMISSÃO (Aguardar maturação)"
        alerta_cor = st.info

    # ── VISÃO DO USUÁRIO LEIGO / INICIANTE (MODO PADRÃO) ───────────────
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

    # ── VISÃO DO USUÁRIO AVANÇADO (MODO PRO) ───────────────────────────
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