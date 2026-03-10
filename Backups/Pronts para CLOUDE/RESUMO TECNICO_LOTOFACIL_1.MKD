# 📘 LotoFácil Pro – Documento de Resumo Técnico  
**Projeto Python – Sistema de Geração e Validação Estatística de Jogos**

---

# 1️⃣ Visão Geral do Projeto

## 🎯 Objetivo Principal

O objetivo do sistema **LotoFácil Pro** é desenvolver um motor estatístico inteligente para geração de jogos da LotoFácil, com base em análise histórica, estratégias configuráveis e validação por backtest comparativo.

O sistema não gera combinações aleatórias puras. Ele:

- Aplica critérios probabilísticos e estruturais
- Controla padrões como repetição, distribuição e recência
- Mede desempenho estatístico real via backtest
- Evolui com base em dados históricos

---

# 2️⃣ Funcionalidades Já Implementadas

## 🧠 Motor Probabilístico

- Geração de jogos com base em histórico de concursos
- Controle de repetição em relação ao último concurso
- Sistema de pontuação (score)
- Modos estratégicos:
  - CONSERVADOR
  - BALANCEADO
  - AGRESSIVO

Cada modo altera:
- Limite máximo de repetição
- Peso de recência
- Penalização aplicada no score

---

## 📊 Sistema de Backtest Comparativo

Execução automática para:

- 200 concursos históricos
- 10 jogos por concurso
- Comparação entre os 3 modos estratégicos

Métricas calculadas:

- Média de acertos
- Desvio padrão
- % de 11+
- % de 12+
- % de 13+
- % de 14+
- Melhor resultado obtido

Atualmente são gerados aproximadamente 2000 jogos por modo (6000 no total por execução comparativa).

---

## 💾 Persistência de Dados

- Banco SQLite
- Estrutura relacional simples
- Tabela principal: `concursos`
- Armazenamento das 15 dezenas por concurso
- Inicialização automática do banco

---

# 3️⃣ Funcionalidades Planejadas

Durante o desenvolvimento foram discutidas as seguintes evoluções:

- V10 – Score Estrutural Avançado
- Penalização dinâmica baseada em:
  - Frequência histórica
  - Atraso individual de dezenas
  - Distribuição par/ímpar
  - Faixa numérica
- Sistema adaptativo que escolhe automaticamente o melhor modo
- Relatórios estatísticos mais detalhados
- Possível versão API futura

---

# 4️⃣ Decisões de Arquitetura

## 🏗 Padrão Arquitetural

Foi adotado um modelo inspirado em:

- Arquitetura em Camadas
- Organização modular
- Separação clara de responsabilidades
- Estrutura próxima de Clean Architecture (simplificada)

---

## 📁 Organização de Pastas

Estrutura principal:

# 📘 LotoFácil Pro – Documento de Resumo Técnico  
**Projeto Python – Sistema de Geração e Validação Estatística de Jogos**

---

# 1️⃣ Visão Geral do Projeto

## 🎯 Objetivo Principal

O objetivo do sistema **LotoFácil Pro** é desenvolver um motor estatístico inteligente para geração de jogos da LotoFácil, com base em análise histórica, estratégias configuráveis e validação por backtest comparativo.

O sistema não gera combinações aleatórias puras. Ele:

- Aplica critérios probabilísticos e estruturais
- Controla padrões como repetição, distribuição e recência
- Mede desempenho estatístico real via backtest
- Evolui com base em dados históricos

---

# 2️⃣ Funcionalidades Já Implementadas

## 🧠 Motor Probabilístico

- Geração de jogos com base em histórico de concursos
- Controle de repetição em relação ao último concurso
- Sistema de pontuação (score)
- Modos estratégicos:
  - CONSERVADOR
  - BALANCEADO
  - AGRESSIVO

Cada modo altera:
- Limite máximo de repetição
- Peso de recência
- Penalização aplicada no score

---

## 📊 Sistema de Backtest Comparativo

Execução automática para:

- 200 concursos históricos
- 10 jogos por concurso
- Comparação entre os 3 modos estratégicos

Métricas calculadas:

- Média de acertos
- Desvio padrão
- % de 11+
- % de 12+
- % de 13+
- % de 14+
- Melhor resultado obtido

Atualmente são gerados aproximadamente 2000 jogos por modo (6000 no total por execução comparativa).

---

## 💾 Persistência de Dados

- Banco SQLite
- Estrutura relacional simples
- Tabela principal: `concursos`
- Armazenamento das 15 dezenas por concurso
- Inicialização automática do banco

---

# 3️⃣ Funcionalidades Planejadas

Durante o desenvolvimento foram discutidas as seguintes evoluções:

- V10 – Score Estrutural Avançado
- Penalização dinâmica baseada em:
  - Frequência histórica
  - Atraso individual de dezenas
  - Distribuição par/ímpar
  - Faixa numérica
- Sistema adaptativo que escolhe automaticamente o melhor modo
- Relatórios estatísticos mais detalhados
- Possível versão API futura

---

# 4️⃣ Decisões de Arquitetura

## 🏗 Padrão Arquitetural

Foi adotado um modelo inspirado em:

- Arquitetura em Camadas
- Organização modular
- Separação clara de responsabilidades
- Estrutura próxima de Clean Architecture (simplificada)

---

## 📁 Organização de Pastas

Estrutura principal:

lotofacil_pro/
│
├── core/
│ ├── domain/
│ │ └── models.py
│ │
│ ├── engine/
│ │ └── probabilistic_engine.py
│ │
│ ├── infrastructure/
│ │ └── database/
│ │ ├── database.py
│ │ └── repository.py
│ │
│ └── avaliacao/
│
├── database/
│ └── lotofacil.db
│
├── main.py
├── rodar_backtest.py


---

## 🔹 Separação de Responsabilidades

### Domain
- Modelos de negócio (ex: Concurso)
- Representa entidades do domínio

### Infrastructure
- Banco de dados
- Conexão SQLite
- Repository pattern para acesso a dados

### Engine
- Lógica de geração de jogos
- Estratégias
- Cálculo de score

### Camada de Aplicação (scripts)
- `main.py` → geração normal
- `rodar_backtest.py` → validação estatística

---

## 🎨 Decisões Importantes de Design

- Uso de classes para encapsular comportamento (ProbabilisticEngine)
- Repository Pattern para acesso ao banco
- Métodos estáticos para evitar necessidade de instanciar objetos
- Separação entre persistência, domínio e lógica de geração
- Uso de `pathlib` para robustez no caminho do banco
- Controle centralizado de configuração de modos

---

# 5️⃣ Bibliotecas Utilizadas

## 📦 Banco de Dados
- `sqlite3`
  - Banco relacional embutido
  - Persistência local

## 📊 Estatística
- `statistics` (stdlib)
  - mean
  - pstdev

## 📁 Utilitários
- `pathlib`
  - Manipulação robusta de caminhos

## 🔁 Tipagem
- `typing`
  - List
  - Tuple
  - Optional

Nenhum framework web foi implementado ainda (FastAPI, Flask etc. não estão sendo usados neste estágio).

---

# 6️⃣ Persistência de Dados

- Tipo: Banco relacional
- Tecnologia: SQLite
- Arquivo físico: `database/lotofacil.db`
- Criação automática de tabelas
- Controle de diretório automático via pathlib

---

# 7️⃣ Tratamento de Erros

Atualmente:

- Uso de exceções padrão do Python
- Correções estruturais para problemas de import e path
- Não existe ainda camada centralizada de tratamento de exceções

Melhoria recomendada:

- Blocos try/except estruturados
- Criação de exceções customizadas
- Logging estruturado

---

# 8️⃣ Sistema de Log

Atualmente:

- Apenas `print()` para saída informativa
- Não existe logging estruturado

Recomendação:

- Implementar módulo `logging`
- Separar níveis (DEBUG, INFO, WARNING, ERROR)
- Gerar arquivo `.log` para auditoria

---

# 9️⃣ Pontos Fracos Identificados

1. Score ainda simplificado (modelo linear)
2. Ausência de logging estruturado
3. Ausência de testes automatizados
4. Engine ainda não usa análise histórica profunda (frequência/atraso)
5. Nenhuma camada de configuração externa (ex: config.py)
6. Nenhuma paralelização no backtest

---

# 🔟 Próximos Passos Sugeridos

## 🔥 Melhorias de Arquitetura

- Introduzir camada de configuração central
- Criar módulo dedicado de estatística avançada
- Separar cálculo de score em módulo próprio
- Preparar base para futura API

---

## 🧹 Melhorias de Organização

- Criar pasta `services/` para orquestração
- Padronizar nomenclatura dos módulos
- Consolidar versões antigas de score

---

## 🧪 Testes a Criar

- Testes unitários para:
  - Cálculo de score
  - Controle de repetição
  - Cálculo de acertos
- Teste automatizado de backtest
- Teste de integridade do banco

Framework sugerido:

- `pytest`

---

## 🚀 Refatorações Recomendadas

1. Implementar V10 – Score Estrutural Avançado
2. Criar sistema adaptativo de escolha de modo
3. Introduzir análise histórica real (frequência/atraso)
4. Implementar logging profissional
5. Criar exportação estruturada de métricas (CSV/JSON)
6. Modularizar ainda mais o motor

---

# 🏁 Conclusão

O projeto evoluiu de um simples gerador de combinações para um sistema modular com:

- Arquitetura organizada
- Separação clara de camadas
- Modos estratégicos configuráveis
- Validação estatística comparativa
- Base sólida para evolução científica

O próximo salto técnico depende da evolução do modelo de score e da introdução de estatística estrutural mais profunda.
