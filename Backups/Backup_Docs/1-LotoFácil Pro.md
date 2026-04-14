# LotoFácil Pro

Sistema de análise e geração de jogos para a Lotofácil, com foco em:
- Modelos estatísticos (motores V9 e V10).
- Backtests automatizados.
- Evolução futura para produto SaaS (assinaturas, site, Ads).

Este repositório contém o núcleo técnico do projeto (motores, banco de concursos, scripts de análise e backtest).

---

## 1. Visão Geral

O **LotoFácil Pro** gera combinações de dezenas para a Lotofácil utilizando dois motores principais:

- **V9 – score simplificado (baseline estável)**  
  Motor mais antigo, simples, mas com desempenho consistente e muito bom em backtests.

- **V10 – score estrutural adaptativo (em otimização)**  
  Motor mais sofisticado, que leva em conta múltiplos componentes (frequência, recência, atraso, soma, faixas, repetição, sequências) e é calibrado para imitar e superar o “DNA” estatístico do V9.

O objetivo desta base de código é:
- Validar, via backtest, que o **V10 supera o V9** em desempenho.
- Servir como núcleo que será conectado a um **site comercial** de assinaturas.

---

## 2. Estrutura do Projeto

Estrutura aproximada do repositório:

```bash
lotofacil_pro/
├─ core/
│  ├─ domain/
│  │  └─ models.py          # Modelos de domínio (Concurso, Jogo, etc.)
│  ├─ statistics/
│  │  ├─ score_v9.py        # Implementação do motor V9 (score simplificado)
│  │  └─ score_v10.py       # Implementação do motor V10 (score estrutural adaptativo)
│  ├─ services/
│  │  ├─ gerador_jogos.py   # Lógica de geração de jogos usando V9/V10
│  │  └─ concursos_service.py # Carregamento e atualização de concursos
│  └─ infrastructure/
│     └─ db/
│        ├─ conexao.py      # Acesso ao banco de dados (SQLite/PostgreSQL, etc.)
│        └─ repositorios.py # Repositórios para concursos, jogos, etc.
├─ scripts/
│  ├─ rodar_backtest_v9_v10.py   # Backtest comparativo entre V9 e V10
│  ├─ analisar_motor_v9.py       # Análise de perfil dos jogos gerados pelo V9
│  └─ (futuro) analisar_motor_v10.py # Análise de perfil dos jogos gerados pelo V10
├─ data/
│  ├─ concursos_lotofacil.csv    # Histórico de concursos (se aplicável)
│  └─ cache/                     # Arquivos de cache temporário
├─ venv/                         # Ambiente virtual Python (não versionar)
├─ README.md                     # Este arquivo
└─ requirements.txt              # Dependências do projeto
```

> Obs.: ajuste a árvore conforme a estrutura real do seu repositório.

---

## 3. Instalação e Execução

### 3.1. Pré-requisitos

- Python 3.10+ (recomendado).
- `pip` atualizado.
- (Opcional) Ambiente virtual (`venv`).

### 3.2. Setup do ambiente

```bash
# Clonar o repositório
git clone https://seu-repositorio.git
cd lotofacil_pro

# Criar e ativar o venv (Windows)
python -m venv venv
venv\Scripts\activate

# Ou (Linux/Mac)
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3.3. Atualizar banco de concursos (se aplicável)

Se houver script específico para importar/atualizar concursos, algo como:

```bash
py scripts/atualizar_concursos.py
```

(Adapte para o nome real do script, se existir.)

---

## 4. Motores de Score

### 4.1. Motor V9 – Score Simplificado

- Baseado principalmente em:
  - **Soma das dezenas** (quanto maior a soma, maior o score).
  - Penalização por excesso de repetição com o último concurso.

Perfil medido (exemplo com 2000 jogos):

- Soma média ≈ **221,77** (tende a jogos “mais altos”).
- Pares/ímpares equilibrados (em torno de 7–8 de cada).
- Distribuição por faixas (1–5, 6–10, 11–15, 16–20, 21–25):  
  `1.92, 2.52, 3.02, 3.55, 3.98` (favorece as faixas altas 16–25).
- Repetição com último concurso: média ≈ 7–8 dezenas.

### 4.2. Motor V10 – Score Estrutural Adaptativo

- Considera múltiplos componentes:
  - Frequência histórica.
  - Frequência recente (com ajuste dinâmico por “ciclo”).
  - Atraso.
  - Soma (alvo ≈ 222, imitando V9).
  - Distribuição por faixas (alvo: padrão do V9).
  - Repetição com último concurso (ideal: 7–8 dezenas).
  - Penalização para sequências longas de dezenas consecutivas.

- Implementado em: `core/statistics/score_v10.py`.

---

## 5. Backtests

### 5.1. Script de backtest comparativo

Rodar o comparativo V9 x V10:

```bash
py scripts/rodar_backtest_v9_v10.py
```

Saída típica (exemplo):

```text
==== LotoFácil Pro – Backtest Comparativo V9 x V10 ====

Total de concursos disponíveis: 3632
Modo         : BALANCEADO
Concursos    : 200
Jogos/conc.  : 10
Total jogos  : 2000

Rodando V9...
Rodando V10...

===== RESULTADO COMPARATIVO V9 x V10 =====

Motor       : V9 (score simplificado)
Total jogos : 2000
Média       : 9.056
Desvio      : 1.239
Melhor      : 13
% 11+       : 12.1%
% 12+       : 2.1%
% 13+       : 0.2%

--------------------------------------------------
Motor       : V10 (score estrutural adaptativo)
Total jogos : 2000
Média       : 9.045
Desvio      : 1.202
Melhor      : 13
% 11+       : 10.9%
% 12+       : 2.1%
% 13+       : 0.1%

Diferença de média V10 - V9: -0.011
```

> A meta é que o V10 **supere** o V9, especialmente em:
> - média de acertos,
> - % de jogos com 11+ acertos,
> mantendo ou melhorando o desempenho em 12+.

### 5.2. Análise de perfil do V9

Rodar:

```bash
py scripts/analisar_motor_v9.py
```

Saída esperada: estatísticas de soma, pares/ímpares, faixas e repetição dos jogos gerados pelo V9 (usado como “perfil alvo” para calibrar o V10).

### 5.3. (Futuro) Análise de perfil do V10

Planejado um script similar (`analisar_motor_v10.py`) para:

- Ver se o V10 está replicando o perfil desejado (soma, faixas, repetição).
- Ajustar pesos finos com base em dados, não em “achismo”.

---

## 6. Roadmap Técnico (Fases do Projeto)

### Fase 1 – Núcleo Lotofácil Pro (este repositório)

**Objetivos:**

- Consolidar V9 como baseline.
- Ajustar V10 até que ele seja **consistentemente superior** ao V9 em backtests.

**Critérios de sucesso (exemplo de metas):**

- V10 com:
  - Média ≥ **9.10**.
  - % 11+ ≥ **12.5%**.
  - % 12+ ≥ **2.1%**.
- Tempo de geração de jogo: ≤ 1 s.

---

### Fase 2 – Site e Monetização (fora deste repositório, mas relacionado)

**Objetivos:**

- Criar site com:
  - Landing page.
  - Dashboard para assinantes.
- Integrar:
  - Pagamentos recorrentes (Stripe/Mercado Pago).
  - Google AdSense (páginas de conteúdo).
  - Google Ads (captação de assinantes).

---

### Fase 3 – Expansão para Quina

**Objetivos:**

- Desenvolver `score_quina.py` com lógica similar (frequência, recência, atraso, etc.).
- Integrar Quina ao mesmo dashboard.

---

### Fase 4 – Expansão Mega-Sena

**Objetivos:**

- Motor focado em simulações, padrões e conteúdo educativo.
- Usado como funil de entrada para trazer usuários para Lotofácil/Quina.

---

## 7. Boas Práticas e Avisos

- Este projeto é para **análise estatística e entretenimento**.
- Não há garantia de ganho financeiro em loterias.
- Uso responsável:
  - Não comprometer dinheiro essencial (contas, dívidas, etc.).
- Se integrar com Ads (Google Ads/AdSense) e serviços de pagamento:
  - Atentar às políticas de cada serviço.
  - Atentar à LGPD e demais legislações aplicáveis.

---

## 8. Contribuição

Por enquanto, o foco é o desenvolvimento interno.  
Se futuramente forem abertas contribuições:

- Abrir issues com:
  - descrição clara do bug/melhoria,
  - logs ou prints do problema,
  - contexto (ex.: qual script, qual modo de backtest).
- Sugerir melhorias com:
  - justificativa estatística,
  - impacto esperado em métricas (média, %11+, etc.).

---

## 9. Licença

(Defina aqui a licença do projeto, por exemplo:)

- MIT / Apache 2.0 / Proprietário – a definir.

---