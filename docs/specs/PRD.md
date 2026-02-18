# PRD — PORTFOLIO COCKPIT
## Family Office Investment Monitoring Dashboard

> **Versão:** 1.0
> **Data:** 18/02/2026
> **Autor:** CIO — Comitê de Investimentos
> **Destinatário:** Claude Code (execução em minitasks)

---

## 1. VISÃO GERAL DO PRODUTO

### 1.1 O Que É

Dashboard web de monitoramento de portfólio de investimentos para um family office pessoal que opera sob filosofia GARP (Growth at Reasonable Price). O cockpit centraliza posições, performance, risco, indicadores macro e gestão de teses de investimento em uma interface unificada.

### 1.2 Por Que Existe

O portfólio (~R$514k, ~20 posições entre Brasil e EUA) é atualmente gerido via planilha Excel + documentos markdown avulsos. Não há visão consolidada de risco, correlação entre posições, tracking de teses, ou simulação de cenários. O cockpit substitui esse fluxo manual por uma ferramenta analítica integrada.

### 1.3 Para Quem

Usuário único: o CIO/investidor do family office. Uso semanal, desktop-first com consulta ocasional via mobile.

### 1.4 Princípios de Design

1. **Profundidade analítica > Estética superficial.** Priorizar informação acionável sobre decoração visual.
2. **GARP-centric.** Toda métrica e visualização deve servir à filosofia Quality + Growth.
3. **Dados reais, não mock.** Desde o MVP, alimentar com dados reais do portfólio e APIs de mercado.
4. **Simulação como ferramenta central.** O investidor quer testar cenários ("e se eu vender 50% de X?").
5. **Teses vivas.** O cockpit não é só P&L — é um sistema de gestão de convicção sobre cada posição.

---

## 2. ARQUITETURA TÉCNICA

### 2.1 Stack

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| **Frontend/UI** | Streamlit (Python) | Rápido de desenvolver, nativo para analytics, interativo |
| **Gráficos** | Plotly | Interativos, hover tooltips, responsivos |
| **Backend/Analytics** | Python (Pandas, NumPy) | Ecossistema financeiro maduro |
| **Banco de Dados** | Supabase (PostgreSQL) | Free tier (500MB), API REST, auth embutido |
| **Dados de Mercado BR** | brapi.dev (API gratuita) | Cotações B3, fundamentalistas, dividendos |
| **Dados de Mercado US** | yfinance (Python lib) | Cotações US, histórico, dividendos |
| **Dados Macro** | BCB API + FRED | Selic, IPCA, câmbio, Treasury, DXY |
| **Portfolio Analytics** | PyPortfolioOpt, quantstats | Otimização, risk metrics, performance attribution |
| **Deploy** | Streamlit Cloud (gratuito) | URL pública/privada, HTTPS, zero config |
| **Auth** | Streamlit native (password) ou Supabase Auth | Proteção básica da dashboard |

### 2.2 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT CLOUD                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │              STREAMLIT APP (Python)                │  │
│  │                                                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │ Overview  │ │Positions │ │Risk/Macro│          │  │
│  │  │  Page     │ │  Page    │ │  Page    │          │  │
│  │  └──────────┘ └──────────┘ └──────────┘          │  │
│  │  ┌──────────┐ ┌──────────┐                        │  │
│  │  │ Thesis   │ │Simulator │                        │  │
│  │  │  Board   │ │  Page    │                        │  │
│  │  └──────────┘ └──────────┘                        │  │
│  │                    │                               │  │
│  │          ┌─────────┴─────────┐                    │  │
│  │          │   DATA LAYER      │                    │  │
│  │          │  (Pandas/NumPy)   │                    │  │
│  │          └─────────┬─────────┘                    │  │
│  └────────────────────┼──────────────────────────────┘  │
└────────────────────────┼────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────┴────┐   ┌──────┴──────┐  ┌─────┴─────┐
    │Supabase │   │ Market APIs │  │ Macro APIs│
    │(Postgres)│  │brapi/yfinance│ │ BCB/FRED  │
    └─────────┘   └─────────────┘  └───────────┘
```

### 2.3 Estrutura de Diretórios

```
portfolio-cockpit/
├── CLAUDE.md                           # Regras do projeto para Claude Code
├── ROADMAP.md                          # Estado atual e tasks
├── README.md                           # Documentação do projeto
├── pyproject.toml                      # Dependências e config (uv + ruff + pytest)
├── .gitignore                          # Python + Streamlit + secrets
├── .python-version                     # 3.12
│
├── .streamlit/
│   ├── config.toml                     # Tema e layout Streamlit
│   └── secrets.toml.example            # Template de secrets (sem valores reais)
│
├── .claude/
│   └── commands/
│       ├── start.md                    # /start — início de sessão
│       ├── finish.md                   # /finish — fim de sessão
│       └── git.md                      # /git — workflow git
│
├── app.py                              # Entry point Streamlit (multipage + auth)
│
├── pages/
│   ├── 1_📊_Overview.py
│   ├── 2_💼_Positions.py
│   ├── 3_⚠️_Risk_Macro.py
│   ├── 4_📋_Thesis_Board.py
│   ├── 5_🔬_Simulator.py
│   └── 6_📚_Knowledge_Base.py
│
├── data/
│   ├── __init__.py
│   ├── db.py                           # Conexão Supabase + CRUD
│   ├── market_data.py                  # Cotações BR (brapi) + US (yfinance)
│   ├── macro_data.py                   # Indicadores macro (BCB + yfinance)
│   └── seed.py                         # Popular DB com dados iniciais
│
├── analytics/
│   ├── __init__.py
│   ├── portfolio.py                    # Pesos, P&L, exposição
│   ├── risk.py                         # VaR, correlação, stress tests
│   ├── performance.py                  # Returns, attribution, benchmark
│   └── simulator.py                    # Engine de simulação
│
├── utils/
│   ├── __init__.py
│   ├── formatting.py                   # Formatação de moedas, %, datas
│   ├── constants.py                    # Tickers, setores, benchmarks, cores
│   └── currency.py                     # Conversão BRL/USD
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Fixtures compartilhadas
│   ├── test_portfolio.py
│   ├── test_risk.py
│   └── test_simulator.py
│
├── knowledge_base/                     # Arquivos .md fonte para seed no DB
│   ├── deepdives/                      # 18 deep dives (1 por ticker)
│   │   ├── ALOS3.md
│   │   ├── ASML.md
│   │   ├── BRAV3.md
│   │   ├── ENGI4.md
│   │   ├── EQTL3.md
│   │   ├── GMAT3.md
│   │   ├── GOOGL.md
│   │   ├── INBR32.md
│   │   ├── KLBN4.md
│   │   ├── MELI.md
│   │   ├── MGLU3.md
│   │   ├── MU.md
│   │   ├── NVDA.md
│   │   ├── PLPL3.md
│   │   ├── RAPT4.md
│   │   ├── SNPS.md
│   │   ├── TSM.md
│   │   └── UGPA3.md
│   ├── reports/                        # Relatórios temáticos
│   │   ├── oil_analysis.md
│   │   ├── relatorio_macro_rotacao.md
│   │   ├── relatorio_safra_2025_26.md
│   │   └── tese_suzb3_atualizada.md
│   └── frameworks/                     # Frameworks de referência
│       ├── framework_analise.md
│       └── portfolio_mapeamento.md
│
└── docs/
    ├── specs/
    │   └── PRD.md                      # Este documento
    ├── learnings/
    │   ├── o-que-funciona.md           # Padrões que funcionam
    │   └── armadilhas.md               # Problemas e soluções
    └── decisions/
        └── 001-streamlit-over-react.md # ADR: escolha de Streamlit
```

### 2.4 Abordagem de Desenvolvimento

**Spec-Driven Development (SDD):** Toda implementação segue este PRD como fonte de verdade. Mudanças na spec devem ser propostas e aprovadas antes da implementação.

**Gerenciamento de projeto:**
- `ROADMAP.md` — tasks com status `[ ]`, `[-] 🏗️`, `[x] ✅`
- `CLAUDE.md` — regras do projeto para o Claude Code
- `.claude/commands/` — slash commands (/start, /finish, /git)
- `docs/learnings/` — padrões e armadilhas descobertas durante desenvolvimento
- `docs/decisions/` — ADRs (Architecture Decision Records) para decisões técnicas

**Tooling:**
- Package manager: `uv` (substitui pip + venv)
- Lint + Format: `ruff` (substitui black + isort + flake8)
- Testes: `pytest` (apenas módulos em `analytics/`)
- Git: Conventional Commits em português, branches `feat/`, `fix/`, `refactor/`

**Princípios anti-over-engineering:**
- Solução simples primeiro. Sem abstrações prematuras.
- Funções > classes. Composição > herança.
- Máximo ~50 linhas por função, ~300 linhas por arquivo.
- Sem código "para o futuro". Implementar o que a spec pede.

---

## 3. MODELO DE DADOS (SUPABASE)

### 3.1 Tabela: `positions`

Posições atuais do portfólio. Source of truth para holdings.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `ticker` | text | Ticker (ex: INBR32, NVDA) |
| `company_name` | text | Nome da empresa |
| `market` | text | BR ou US |
| `currency` | text | BRL ou USD |
| `sector` | text | Setor (enum: energia_materiais, utilities, consumo_varejo, tech_semis, financeiro, fundos, caixa) |
| `analyst` | text | Analista responsável (enum dos 7 membros do comitê) |
| `quantity` | decimal | Quantidade de ações/cotas |
| `avg_price` | decimal | Preço médio de aquisição (na moeda original) |
| `total_invested` | decimal | Valor total investido (na moeda original) |
| `dividends_received` | decimal | Proventos acumulados recebidos (na moeda original) |
| `target_weight` | decimal | Peso-alvo no portfólio (%) — definido pelo CIO |
| `is_active` | boolean | Se a posição está ativa |
| `created_at` | timestamp | Data de criação |
| `updated_at` | timestamp | Última atualização |

### 3.2 Tabela: `transactions`

Histórico de transações para auditoria e cálculo de performance.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `position_id` | uuid (FK) | Referência à posição |
| `ticker` | text | Ticker |
| `type` | text | BUY, SELL, DIVIDEND |
| `quantity` | decimal | Quantidade |
| `price` | decimal | Preço da transação |
| `total_value` | decimal | Valor total |
| `currency` | text | BRL ou USD |
| `date` | date | Data da transação |
| `notes` | text | Observações |
| `created_at` | timestamp | Data de criação |

### 3.3 Tabela: `theses`

Teses de investimento por posição. Espelha o framework_analise.md.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `position_id` | uuid (FK) | Referência à posição |
| `ticker` | text | Ticker |
| `status` | text | GREEN, YELLOW, RED |
| `conviction` | text | HIGH, MEDIUM, LOW |
| `summary` | text | Resumo da tese (3-5 linhas) |
| `moat_rating` | text | STRONG, MODERATE, WEAK, NONE |
| `moat_trend` | text | WIDENING, STABLE, NARROWING |
| `growth_drivers` | jsonb | Array de drivers de crescimento |
| `bull_case_price` | decimal | Preço no cenário otimista |
| `base_case_price` | decimal | Preço no cenário base |
| `bear_case_price` | decimal | Preço no cenário pessimista |
| `target_price` | decimal | Preço-alvo ponderado (20/60/20) |
| `kill_switches` | jsonb | Array de condições kill switch |
| `catalysts` | jsonb | Array de catalisadores com datas |
| `key_risks` | jsonb | Array de riscos com probabilidade/impacto |
| `roic_current` | decimal | ROIC atual (%) |
| `wacc_estimated` | decimal | WACC estimado (%) |
| `last_review` | date | Data da última revisão |
| `next_review` | date | Data da próxima revisão obrigatória |
| `review_trigger` | text | Evento que dispara revisão (ex: "Após 4T25") |
| `notes` | text | Notas adicionais |
| `created_at` | timestamp | Data de criação |
| `updated_at` | timestamp | Última atualização |

### 3.4 Tabela: `catalysts`

Calendário de catalisadores separado para visualização timeline.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `ticker` | text | Ticker |
| `description` | text | Descrição do catalisador |
| `expected_date` | date | Data esperada |
| `impact` | text | HIGH, MEDIUM, LOW |
| `category` | text | EARNINGS, REGULATORY, MACRO, CORPORATE, OTHER |
| `completed` | boolean | Se já ocorreu |
| `outcome_notes` | text | O que aconteceu (preenchido após o evento) |
| `created_at` | timestamp | Data de criação |

### 3.5 Tabela: `macro_snapshots`

Snapshots periódicos de indicadores macro para histórico.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `date` | date | Data do snapshot |
| `selic` | decimal | Taxa Selic (%) |
| `ipca_12m` | decimal | IPCA acumulado 12m (%) |
| `usd_brl` | decimal | Câmbio USD/BRL |
| `dxy` | decimal | Índice Dólar |
| `ibov` | decimal | Ibovespa pontos |
| `sp500` | decimal | S&P 500 pontos |
| `vix` | decimal | VIX |
| `brent` | decimal | Preço Brent (USD/bbl) |
| `cellulose_bhkp` | decimal | Preço celulose BHKP (USD/ton) |
| `treasury_10y` | decimal | Treasury 10Y yield (%) |
| `di_jan27` | decimal | DI Futuro Jan/2027 (%) |
| `cds_brazil_5y` | decimal | CDS Brasil 5 anos (bps) |
| `created_at` | timestamp | Data de criação |

### 3.6 Tabela: `deep_dives`

Armazena cada versão de deep dive por ticker. Permite rastrear evolução analítica ao longo do tempo.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `ticker` | text | Ticker da posição |
| `version` | integer | Versão sequencial (1, 2, 3...) — auto-increment por ticker |
| `title` | text | Título do deep dive (ex: "DEEP DIVE — INBR32 — Inter & Co") |
| `analyst` | text | Analista responsável |
| `content_md` | text | Conteúdo completo do deep dive em Markdown |
| `summary` | text | Resumo executivo (3-5 linhas extraídas do doc) |
| `thesis_status_at_time` | text | Status da tese no momento do deep dive (GREEN/YELLOW/RED) |
| `conviction_at_time` | text | Convicção no momento (HIGH/MEDIUM/LOW) |
| `target_price_at_time` | decimal | Preço-alvo no momento do deep dive |
| `current_price_at_time` | decimal | Cotação no momento do deep dive |
| `key_metrics` | jsonb | Snapshot de métricas-chave (ROIC, WACC, P/E, EV/EBITDA, etc.) |
| `key_changes` | text | O que mudou vs. versão anterior (preenchido a partir da v2) |
| `tags` | text[] | Tags para busca (ex: ["earnings", "regulatory", "thesis_update"]) |
| `date` | date | Data do deep dive |
| `created_at` | timestamp | Data de criação |

**Lógica de versionamento:** Cada novo deep dive para o mesmo ticker incrementa `version`. A versão mais recente é a "vigente". Versões anteriores são preservadas para consulta histórica.

### 3.7 Tabela: `analysis_reports`

Armazena relatórios temáticos (macro, setoriais, oil analysis, safra, etc.) que não são específicos de um ticker.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `title` | text | Título do relatório |
| `report_type` | text | MACRO, SECTOR, THEMATIC, PORTFOLIO_REVIEW |
| `content_md` | text | Conteúdo completo em Markdown |
| `summary` | text | Resumo executivo |
| `tickers_mentioned` | text[] | Tickers referenciados no relatório |
| `tags` | text[] | Tags para busca |
| `date` | date | Data do relatório |
| `created_at` | timestamp | Data de criação |

### 3.8 Tabela: `portfolio_snapshots`

Snapshots do portfólio para cálculo de performance ao longo do tempo.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid (PK) | ID único |
| `date` | date | Data do snapshot |
| `total_value_brl` | decimal | Patrimônio total em BRL |
| `total_value_usd` | decimal | Patrimônio total em USD |
| `cash_brl` | decimal | Caixa em BRL |
| `positions_data` | jsonb | Snapshot completo de cada posição (ticker, qty, price, value) |
| `ibov_value` | decimal | Valor do Ibovespa no dia |
| `cdi_accumulated` | decimal | CDI acumulado desde início |
| `created_at` | timestamp | Data de criação |

---

## 4. DADOS INICIAIS — POSIÇÕES ATUAIS (SEED)

Dados extraídos de `portfolio_unico_1.xlsx` em 18/02/2026.

### 4.1 Ações Brasileiras (BRL)

| Ticker | Empresa | Setor | Qtd | Cotação | PM | Investido | Saldo | Dividendos |
|--------|---------|-------|-----|---------|------|-----------|-------|------------|
| INBR32 | Inter & Co Inc. | financeiro | 1.905 | 46,81 | 32,67 | 62.244,54 | 89.173,05 | 503,37 |
| ENGI4 | Energisa | utilities | 4.390 | 10,00 | 8,04 | 35.280,47 | 43.900,00 | 5.354,85 |
| EQTL3 | Equatorial | utilities | 642 | 41,37 | 31,23 | 20.052,57 | 26.559,54 | 1.529,79 |
| ALOS3 | Aliansce Sonae | consumo_varejo | 800 | 31,15 | 18,87 | 15.092,91 | 24.920,00 | 1.439,85 |
| SUZB3 | Suzano | energia_materiais | 400 | 58,25 | 51,04 | 20.414,94 | 23.300,00 | 699,11 |
| KLBN4 | Klabin | energia_materiais | 5.383 | 4,07 | 3,73 | 20.097,16 | 21.908,81 | 1.937,48 |
| BRAV3 | Brava Energia | energia_materiais | 1.000 | 17,59 | 15,86 | 15.858,00 | 17.590,00 | 0,00 |
| PLPL3 | Plano & Plano | consumo_varejo | 1.100 | 15,70 | 13,72 | 15.088,68 | 17.270,00 | 0,00 |
| RAPT4 | Empresas Randon | consumo_varejo | 2.500 | 6,31 | 6,02 | 15.057,67 | 15.775,00 | 0,00 |
| GMAT3 | Grupo Mateus | consumo_varejo | 2.600 | 5,23 | 4,91 | 12.773,07 | 13.598,00 | 0,00 |

### 4.2 Ações Internacionais (USD)

| Ticker | Empresa | Setor | Qtd | Cotação | PM | Investido | Saldo |
|--------|---------|-------|-----|---------|------|-----------|-------|
| TSM | Taiwan Semiconductor | tech_semis | 10,51 | 357,00 | 333,01 | 3.499,26 | 3.751,66 |
| NVDA | Nvidia | tech_semis | 15,69 | 191,00 | 191,23 | 2.999,99 | 2.996,32 |
| ASML | ASML Holding | tech_semis | 1,51 | 1.436,00 | 1.455,97 | 2.199,98 | 2.169,69 |
| MELI | MercadoLibre | tech_semis | 0,64 | 2.018,00 | 2.193,50 | 1.403,84 | 1.291,08 |
| GOOGL | Alphabet | tech_semis | 3,85 | 313,00 | 259,84 | 1.000,65 | 1.205,05 |
| SNPS | Synopsys | tech_semis | 2,47 | 438,00 | 485,24 | 1.199,99 | 1.083,17 |
| MU | Micron Technology | tech_semis | 2,21 | 386,00 | 405,17 | 896,24 | 853,83 |

### 4.3 Outros Ativos

| Classe | Descrição | Moeda | Valor (R$) |
|--------|-----------|-------|------------|
| fundos | FIDC Microcrédito | BRL | 14.565,79 |
| fundos | BTG Eletrobrás FMP | BRL | 36.864,92 |
| caixa | Cofrinhos | BRL | 91.798,00 |

### 4.4 Resumo Patrimonial

| Classe | Valor (R$) | % Portfólio |
|--------|-----------|-------------|
| Ações BR | 293.994,40 | 57,2% |
| Ações US (R$) | 76.767,10 | 14,9% |
| FIDC Microcrédito | 14.565,79 | 2,8% |
| BTG Eletrobrás FMP | 36.864,92 | 7,2% |
| Caixa | 91.798,00 | 17,9% |
| **TOTAL** | **513.990,21** | **100%** |

**Nota:** Câmbio de referência: USD 1 = BRL 5,75

### 4.5 Mapeamento Setor → Analista

| Setor (DB) | Analista | Tickers |
|------------|----------|---------|
| energia_materiais | Analista de Energia & Materiais | BRAV3, SUZB3, KLBN4, UGPA3 |
| utilities | Analista de Utilities & Concessões | ENGI4, EQTL3, BTG Eletrobrás FMP |
| consumo_varejo | Analista de Consumo, Varejo & Imobiliário | GMAT3, ALOS3, PLPL3, RAPT4 |
| tech_semis | Analista de Tecnologia & Semicondutores | TSM, NVDA, ASML, MELI, GOOGL, SNPS, MU |
| financeiro | Analista Financeiro & Crédito | INBR32, FIDC Microcrédito |

### 4.6 Knowledge Base — Seed Data (Deep Dives Existentes)

18 deep dives já produzidos pelo Comitê + 4 relatórios temáticos. Todos localizados na pasta `knowledge_base/` do projeto. O `seed.py` deve:

1. Ler cada arquivo `.md` da pasta `knowledge_base/deepdives/`
2. Extrair metadados do cabeçalho (título, data, analista)
3. Inserir na tabela `deep_dives` como version=1 para cada ticker
4. Ler cada arquivo `.md` da pasta `knowledge_base/reports/`
5. Inserir na tabela `analysis_reports` com tipo e tags inferidos

**Deep Dives disponíveis (18 arquivos, ~677KB total):**

| Arquivo | Ticker | Tamanho | Setor |
|---------|--------|---------|-------|
| INBR32.md | INBR32 | 20KB | financeiro |
| ENGI4.md | ENGI4 | 36KB | utilities |
| EQTL3.md | EQTL3 | 33KB | utilities |
| ALOS3.md | ALOS3 | 29KB | consumo_varejo |
| SUZB3.md* | SUZB3 | 19KB | energia_materiais |
| KLBN4.md | KLBN4 | 29KB | energia_materiais |
| BRAV3.md | BRAV3 | 27KB | energia_materiais |
| UGPA3.md | UGPA3 | 35KB | energia_materiais |
| PLPL3.md | PLPL3 | 31KB | consumo_varejo |
| RAPT4.md | RAPT4 | 29KB | consumo_varejo |
| GMAT3.md | GMAT3 | 32KB | consumo_varejo |
| MGLU3.md | MGLU3 | 32KB | consumo_varejo |
| TSM.md | TSM | 28KB | tech_semis |
| NVDA.md | NVDA | 35KB | tech_semis |
| ASML.md | ASML | 31KB | tech_semis |
| MELI.md | MELI | 32KB | tech_semis |
| GOOGL.md | GOOGL | 27KB | tech_semis |
| SNPS.md | SNPS | 36KB | tech_semis |
| MU.md | MU | 29KB | tech_semis |

*SUZB3: arquivo `tese_suzb3_atualizada.md` em reports/ (formato diferente, tratar como deep dive)

**Relatórios temáticos (4 arquivos):**

| Arquivo | Tipo | Tags sugeridas |
|---------|------|----------------|
| oil_analysis.md | SECTOR | oil, brent, energy, brav3 |
| relatorio_macro_rotacao.md | MACRO | selic, rotacao, macro, ciclo |
| relatorio_safra_2025_26.md | THEMATIC | agro, safra, commodities |
| tese_suzb3_atualizada.md | SECTOR | celulose, suzb3, export |

**Lógica do seed para deep dives:**
```python
# Pseudocódigo
for file in knowledge_base/deepdives/*.md:
    ticker = file.stem  # INBR32, ENGI4, etc.
    content = file.read_text()
    title = extract_first_h1(content)  # "# DEEP DIVE — INBR32 — Inter & Co"
    summary = extract_section(content, "RESUMO DA TESE")
    
    # Extrair métricas-chave do conteúdo (ROIC, target, etc.)
    key_metrics = parse_metrics_from_content(content)
    
    insert_deep_dive(
        ticker=ticker,
        version=1,
        title=title,
        content_md=content,
        summary=summary,
        key_metrics=key_metrics,
        date="2026-02-18",  # data do seed
        tags=["initial_deep_dive", sector_for_ticker(ticker)]
    )
```

### 4.7 Mapeamento Fator de Risco → Posições

| Fator | Tickers Expostos | Direção |
|-------|-----------------|---------|
| Selic / Juros BR | ENGI4, EQTL3, ALOS3, PLPL3, INBR32 | Inversa (Selic↓ = positivo) |
| USD/BRL | SUZB3, KLBN4, BRAV3 | Positiva (BRL↓ = positivo) |
| USD/BRL | TSM, NVDA, ASML, MELI, GOOGL, SNPS, MU | Negativa em BRL (BRL↓ = negativo convertido) |
| Brent | BRAV3 | Positiva |
| Celulose BHKP | SUZB3, KLBN4 | Positiva |
| Ciclo Semicondutores | TSM, NVDA, ASML, SNPS, MU | Positiva |
| Crédito Consumidor | PLPL3, INBR32 | Positiva |
| Consumo/Varejo | ALOS3, GMAT3, RAPT4 | Positiva |

---

## 5. APIs E FONTES DE DADOS

### 5.1 Cotações Brasil — brapi.dev

```
Base URL: https://brapi.dev/api
Endpoint: /quote/{tickers}
Método: GET
Rate limit: 15 req/min (free tier)
Dados: preço atual, variação dia, volume, min/max 52s
Tickers: INBR32, ENGI4, EQTL3, ALOS3, SUZB3, KLBN4, BRAV3, PLPL3, RAPT4, GMAT3
Nota: brapi requer token gratuito (cadastro no site)
```

**Fallback:** yfinance com sufixo `.SA` (ex: `INBR32.SA`)

### 5.2 Cotações EUA — yfinance

```python
import yfinance as yf
tickers = ["TSM", "NVDA", "ASML", "MELI", "GOOGL", "SNPS", "MU"]
data = yf.download(tickers, period="1d")
```

Dados: preço, histórico, dividendos, fundamentalistas básicos
Rate limit: sem limite formal, mas usar cache agressivo

### 5.3 Câmbio USD/BRL — BCB API

```
URL: https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json
Série 1 = PTAX venda
```

### 5.4 Indicadores Macro Brasil — BCB SGS

| Indicador | Série BCB | Frequência |
|-----------|-----------|------------|
| Selic Meta | 432 | Diária |
| IPCA mensal | 433 | Mensal |
| IPCA acumulado 12m | 13522 | Mensal |
| CDI acumulado | 12 | Diária |
| Câmbio PTAX | 1 | Diária |

### 5.5 Indicadores Macro Global — yfinance / FRED

| Indicador | Fonte | Ticker yfinance |
|-----------|-------|-----------------|
| S&P 500 | yfinance | ^GSPC |
| VIX | yfinance | ^VIX |
| DXY | yfinance | DX-Y.NYB |
| Brent | yfinance | BZ=F |
| Treasury 10Y | yfinance | ^TNX |
| Ibovespa | yfinance | ^BVSP |

### 5.6 Celulose BHKP

```
Fonte primária: yfinance não tem celulose diretamente.
Alternativa: scraping de fastmarkets.com ou input manual periódico.
Decisão: campo de input manual no dashboard (atualizado semanalmente pelo usuário).
```

---

## 6. PÁGINAS DO DASHBOARD — ESPECIFICAÇÃO DETALHADA

### 6.1 Página: Overview (Home)

**Objetivo:** Visão de helicóptero do portfólio. O investidor abre e em 10 segundos sabe como está.

**Layout:**

```
┌────────────────────────────────────────────────────────┐
│  🏦 PORTFOLIO COCKPIT              [BRL ▼] [Refresh]  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Patrimônio│ │ P&L Total│ │P&L Mês   │ │  Caixa   │ │
│  │ R$514.0k │ │ +R$73.5k │ │ +R$12.3k │ │ R$91.8k  │ │
│  │          │ │  +14.3%  │ │  +2.4%   │ │  17.9%   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                        │
│  ┌─────────────────────┐ ┌────────────────────────┐   │
│  │  ALOCAÇÃO SETORIAL  │ │   TOP MOVERS (semana)  │   │
│  │   (Donut Chart)     │ │                        │   │
│  │                     │ │  🟢 ALOS3    +3.2%    │   │
│  │  ■ Financeiro 20.1% │ │  🟢 INBR32   +2.1%    │   │
│  │  ■ Utilities  20.9% │ │  🔴 MELI     -1.8%    │   │
│  │  ■ Consumo    18.0% │ │  🔴 MU       -1.2%    │   │
│  │  ■ Energia    16.9% │ │                        │   │
│  │  ■ Tech       14.9% │ │                        │   │
│  │  ■ Caixa       8.9% │ │                        │   │
│  └─────────────────────┘ └────────────────────────┘   │
│                                                        │
│  ┌─────────────────────┐ ┌────────────────────────┐   │
│  │ PERFORMANCE vs IBOV │ │  PRÓXIMOS CATALISADORES│   │
│  │   (Line Chart)      │ │                        │   │
│  │                     │ │  📅 19/02 MELI Q4      │   │
│  │  Portfolio ── IBOV  │ │  📅 25/02 ENGI4 Q4     │   │
│  │  ── CDI             │ │  📅 Mar/26 ANEEL rev.  │   │
│  │                     │ │                        │   │
│  └─────────────────────┘ └────────────────────────┘   │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  EXPOSIÇÃO POR FATOR DE RISCO (Barras Horiz.)   │  │
│  │  Selic/Juros    ████████████████░░░░  45%       │  │
│  │  USD/BRL        ██████████████░░░░░░  32%       │  │
│  │  Crédito PF     █████████░░░░░░░░░░░  25%       │  │
│  │  Commodities    ██████░░░░░░░░░░░░░░  17%       │  │
│  │  Semicondutores ██░░░░░░░░░░░░░░░░░░  4.5%     │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**Componentes detalhados:**

1. **KPI Cards (topo):**
   - Patrimônio Total (BRL e USD toggle)
   - P&L Total (R$ e %) — desde início
   - P&L Mês (R$ e %)
   - Caixa Disponível (R$ e % do portfólio)

2. **Donut Chart — Alocação Setorial:**
   - Segmentos: Financeiro, Utilities, Consumo/Varejo, Energia/Materiais, Tech/Semis, Caixa, Fundos
   - Hover mostra: valor em R$, nº de posições, top holding

3. **Top Movers — Semana:**
   - Top 3 gainers e top 3 losers (por % variação na semana)
   - Cor verde/vermelho com ticker e %

4. **Line Chart — Performance vs Benchmark:**
   - 3 linhas: Portfólio, IBOV, CDI (acumulado)
   - Time range selector: 1M, 3M, 6M, YTD, 1A, Início
   - Tooltip com valores

5. **Barras Horizontais — Exposição por Fator:**
   - Calculado a partir do mapeamento fator→posições (seção 4.6)
   - Mostra % do portfólio exposto a cada fator

6. **Próximos Catalisadores:**
   - Lista dos 5 próximos catalisadores por data
   - Puxa da tabela `catalysts` onde `completed = false`
   - Mostra: data, ticker, descrição curta, impacto (cor)

**Toggle de moeda (global):**
- Botão no header: BRL | USD
- Quando USD selecionado, converte todos os valores pela PTAX do dia
- Persiste a preferência na sessão

---

### 6.2 Página: Positions

**Objetivo:** Visão detalhada de cada posição. A "mesa de operações" do investidor.

**Layout:**

```
┌────────────────────────────────────────────────────────────────────────┐
│  💼 POSITIONS                    [Filtro Setor ▼] [Filtro Status ▼]   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Ticker │ Empresa     │ Setor  │ Peso │Target│ Preço │  PM  │P&L│ │
│  │        │             │        │ Atual│ Peso │ Atual │      │ % │ │
│  │────────│─────────────│────────│──────│──────│───────│──────│───│ │
│  │ INBR32 │ Inter & Co  │ Fin.   │17.3% │ 15%  │46.81 │32.67│+44│ │
│  │ ENGI4  │ Energisa    │ Util.  │ 8.5% │  9%  │10.00 │ 8.04│+40│ │
│  │ ...    │             │        │      │      │      │     │   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  Colunas completas (scroll horizontal se necessário):                  │
│  Ticker | Empresa | Setor | Tese 🟢🟡🔴 | Convicção | Peso Atual |   │
│  Peso Target | Gap (peso atual - target) | Qtd | Preço Atual |        │
│  Preço Médio | P&L R$ | P&L % | P&L c/ Div % | Dividendos R$ |       │
│  Próximo Catalisador | Kill Switch Principal | ROIC | WACC |          │
│  Upside ao Target |                                                    │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ DETALHES DA POSIÇÃO SELECIONADA (expande ao clicar na linha)    │ │
│  │                                                                  │ │
│  │ ┌──────────┐ ┌──────────────────┐ ┌───────────────────────────┐│ │
│  │ │Price     │ │ Tese Resumida    │ │ Cenários de Valuation    ││ │
│  │ │Chart     │ │ (do DB theses)   │ │ Bull: R$XX (+XX%)        ││ │
│  │ │(6M hist) │ │                  │ │ Base: R$XX (+XX%)        ││ │
│  │ │          │ │ Kill Switches:   │ │ Bear: R$XX (-XX%)        ││ │
│  │ │          │ │ • Switch 1       │ │ Target: R$XX (+XX%)      ││ │
│  │ │          │ │ • Switch 2       │ │ Margem Seg.: XX%         ││ │
│  │ └──────────┘ └──────────────────┘ └───────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

**Funcionalidades:**

1. **Tabela Principal:**
   - Sortable por qualquer coluna (click no header)
   - Filtro por setor (dropdown multi-select)
   - Filtro por status da tese (🟢🟡🔴)
   - Conditional formatting: P&L positivo verde, negativo vermelho
   - Peso atual > target = highlight amarelo (overweight)
   - Peso atual < target = highlight azul (underweight)
   - Coluna "Gap" mostra diferença peso atual vs target

2. **Seção de Detalhes (expansível):**
   - Gráfico de preço 6M com linha de preço médio de compra
   - Resumo da tese + kill switches (puxa do DB)
   - Cenários bull/base/bear com % upside/downside
   - Margem de segurança calculada

3. **Posições internacionais:**
   - Exibir retorno em USD + retorno em BRL (duas colunas)
   - Coluna "Impacto Câmbio" = diferença entre retorno USD e retorno BRL

4. **Export:**
   - Botão para exportar tabela em CSV

---

### 6.3 Página: Risk & Macro

**Objetivo:** Painel de risco do portfólio e monitoramento de indicadores macro.

**Layout (2 abas internas):**

**Aba 1: Macro Dashboard**

```
┌────────────────────────────────────────────────────────┐
│  ⚠️ RISK & MACRO            [Aba: Macro] [Aba: Risk]  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Selic   │ │USD/BRL   │ │  IBOV    │ │  VIX     │ │
│  │  13.25%  │ │  5.75    │ │ 128.450  │ │  15.2    │ │
│  │  (→)     │ │ (+0.3%)  │ │ (+1.2%)  │ │ (-0.5)  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Brent   │ │  DXY     │ │ S&P 500  │ │IPCA 12m  │ │
│  │ US$74.2  │ │  106.8   │ │  6.117   │ │  4.56%   │ │
│  │ (-1.1%)  │ │ (-0.2%)  │ │ (+0.8%)  │ │  (↑)     │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CURVA DE JUROS IMPLÍCITA (DI Futuro)           │  │
│  │  (Line chart: DI Jan26, Jan27, Jan28, Jan29)    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  MATRIZ MACRO → IMPACTO NO PORTFÓLIO            │  │
│  │                                                   │  │
│  │  Se Selic subir 1pp:    Portfólio estimado: -X%  │  │
│  │  Se BRL depreciar 10%:  Portfólio estimado: +X%  │  │
│  │  Se Brent cair 20%:     Portfólio estimado: -X%  │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**Aba 2: Risk Dashboard**

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CORRELATION MATRIX (Heatmap)                    │  │
│  │  (Retornos 90 dias, todas as posições BR + US)  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────────────┐ ┌────────────────────────┐  │
│  │ CONCENTRAÇÃO         │ │ DIVERSIFICAÇÃO         │  │
│  │                      │ │                        │  │
│  │ HHI: 0.XX            │ │ Top 1: XX%             │  │
│  │ (Baixo/Médio/Alto)   │ │ Top 3: XX%             │  │
│  │                      │ │ Top 5: XX%             │  │
│  │ Efetivo Nº Posições: │ │ Nº Setores: X          │  │
│  │ XX (1/HHI)           │ │ Nº Moedas: 2           │  │
│  └──────────────────────┘ └────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  DRAWDOWN CHART (Max Drawdown do portfólio)     │  │
│  │  (Area chart: drawdown % ao longo do tempo)     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  RISK METRICS                                    │  │
│  │  Sharpe Ratio (vs CDI): X.XX                    │  │
│  │  Sortino Ratio: X.XX                            │  │
│  │  Max Drawdown: -X.X%                            │  │
│  │  Volatilidade 30d: X.X%                         │  │
│  │  Beta vs IBOV: X.XX                             │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**Funcionalidades:**

1. **Macro KPI Cards:** Atualização via APIs (BCB, yfinance). Seta de tendência (↑↓→)
2. **Correlation Heatmap:** Plotly heatmap com retornos diários 90d. Tooltips com valor exato
3. **Stress Test Matrix:** Sensibilidade estimada do portfólio a choques macro (baseada em correlações históricas e betas setoriais)
4. **Risk Metrics:** Calculados via quantstats sobre série histórica de retornos
5. **HHI (Herfindahl-Hirschman Index):** Medida de concentração. <0.10 = diversificado, 0.10-0.18 = moderado, >0.18 = concentrado

---

### 6.4 Página: Thesis Board

**Objetivo:** Gestão de teses de investimento. Visualizar, editar e monitorar convicção por posição.

**Layout:**

```
┌────────────────────────────────────────────────────────┐
│  📋 THESIS BOARD               [+ Nova Tese] [Export] │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─── 🟢 ATIVA ───┐ ┌─── 🟡 REVISÃO ──┐ ┌─ 🔴 ──┐  │
│  │                 │ │                  │ │        │  │
│  │ ┌─────────────┐ │ │ ┌──────────────┐ │ │        │  │
│  │ │ INBR32      │ │ │ │ BRAV3        │ │ │ (vazio)│  │
│  │ │ Conv: ALTA  │ │ │ │ Conv: MÉDIA  │ │ │        │  │
│  │ │ Moat: MOD.  │ │ │ │ Moat: FRACO  │ │ │        │  │
│  │ │ Upside: 25% │ │ │ │ Upside: 40%  │ │ │        │  │
│  │ │ Rev: 15/03  │ │ │ │ Rev: 01/03   │ │ │        │  │
│  │ └─────────────┘ │ │ └──────────────┘ │ │        │  │
│  │ ┌─────────────┐ │ │ ┌──────────────┐ │ │        │  │
│  │ │ ENGI4       │ │ │ │ GMAT3        │ │ │        │  │
│  │ │ ...         │ │ │ │ ...          │ │ │        │  │
│  │ └─────────────┘ │ │ └──────────────┘ │ │        │  │
│  └─────────────────┘ └──────────────────┘ └────────┘  │
│                                                        │
│  ═══════════ DETALHES DA TESE (ao clicar) ══════════  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ INBR32 — Inter & Co Inc.                         │  │
│  │                                                   │  │
│  │ Status: [🟢▼]  Convicção: [ALTA▼]               │  │
│  │                                                   │  │
│  │ Resumo da Tese:                                   │  │
│  │ [campo de texto editável]                         │  │
│  │                                                   │  │
│  │ Moat: [MODERATE▼]  Trend: [WIDENING▼]            │  │
│  │                                                   │  │
│  │ ROIC: [XX%]  WACC: [XX%]  Spread: [auto calc]   │  │
│  │                                                   │  │
│  │ Cenários:                                         │  │
│  │ Bull: [R$ ___] Base: [R$ ___] Bear: [R$ ___]     │  │
│  │ Target (calc): R$ XX.XX  Upside: XX%             │  │
│  │ Margem de Segurança: XX%                          │  │
│  │                                                   │  │
│  │ Catalisadores:                                    │  │
│  │ [+ Adicionar catalisador]                         │  │
│  │ 1. Q4 2025 Results — 19/02/2026 — ALTO           │  │
│  │ 2. Ciclo Selic — Mar/2026 — MÉDIO                │  │
│  │                                                   │  │
│  │ Kill Switches:                                    │  │
│  │ [+ Adicionar kill switch]                         │  │
│  │ 1. ROIC cair abaixo de WACC por 2 trimestres     │  │
│  │ 2. Inadimplência subir acima de X%                │  │
│  │                                                   │  │
│  │ Riscos:                                           │  │
│  │ [+ Adicionar risco]                               │  │
│  │ 1. Competição de incumbentes — Prob: Média — Imp: │  │
│  │                                                   │  │
│  │ Próxima Revisão: [date picker]                    │  │
│  │ Trigger: [text field]                             │  │
│  │                                                   │  │
│  │ [💾 Salvar] [🗑️ Excluir Tese]                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CATALYST CALENDAR (Timeline)                    │  │
│  │  (Gantt-style ou timeline dos próximos 90 dias) │  │
│  │                                                   │  │
│  │  Fev ──────── Mar ──────── Abr ──────── Mai     │  │
│  │  │MELI Q4     │ANEEL        │INBR32 Q1  │       │  │
│  │  │ENGI4 Q4    │Selic COPOM  │SUZB3 Q1   │       │  │
│  │  │            │BRAV3 prod.  │           │       │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**Funcionalidades:**

1. **Kanban por Status:** Cards organizados em 3 colunas (🟢🟡🔴)
2. **Card resumido:** Ticker, convicção, moat rating, upside ao target, próxima revisão
3. **Formulário de edição completo:** Todos os campos da tabela `theses` editáveis via forms Streamlit
4. **CRUD de catalisadores:** Adicionar/editar/remover catalisadores com data e impacto
5. **CRUD de kill switches:** Adicionar/editar/remover condições
6. **Cálculo automático:** Target price = (Bull×20% + Base×60% + Bear×20%). Margem de segurança = (Target - Atual) / Target
7. **Catalyst Timeline:** Visualização temporal dos próximos catalisadores (Plotly timeline)
8. **Alertas:** Highlight em posições com revisão vencida (next_review < today)

---

### 6.5 Página: Simulator

**Objetivo:** Testar cenários de portfólio. "What if" analysis.

**Layout:**

```
┌────────────────────────────────────────────────────────┐
│  🔬 SIMULATOR                                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─── TIPO DE SIMULAÇÃO ───────────────────────────┐  │
│  │ ○ Rebalanceamento   ○ Stress Test   ○ New Trade │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ═══════ REBALANCEAMENTO ═══════                       │
│                                                        │
│  Ajuste os pesos-alvo e veja o impacto:               │
│  ┌────────────────────────────────────────────────┐   │
│  │ INBR32  [===|===============] 17.3% → [15.0%]  │   │
│  │ ENGI4   [===|=========]       8.5% → [ 9.0%]  │   │
│  │ EQTL3   [===|=====]           5.2% → [ 5.0%]  │   │
│  │ ...                                             │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  Resultado:                                            │
│  ┌────────────────────────────────────────────────┐   │
│  │ Trades necessários:                             │   │
│  │ VENDER 200 INBR32 (~R$9.362)                   │   │
│  │ COMPRAR 220 ENGI4 (~R$2.200)                   │   │
│  │ ...                                             │   │
│  │                                                 │   │
│  │ Impacto em concentração: HHI 0.XX → 0.XX       │   │
│  │ Impacto em exposição Selic: 45% → 43%          │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  ═══════ STRESS TEST ═══════                           │
│                                                        │
│  Cenário:                                              │
│  ┌────────────────────────────────────────────────┐   │
│  │ Selic:   [slider: -2% a +3%]  → +1.5%         │   │
│  │ USD/BRL: [slider: -15% a +20%] → +10%         │   │
│  │ Brent:   [slider: -30% a +30%] → -20%         │   │
│  │ IBOV:    [slider: -25% a +25%] → -10%         │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  Impacto estimado no portfólio:                        │
│  ┌────────────────────────────────────────────────┐   │
│  │ Patrimônio estimado: R$XXX.XXX (-X.X%)         │   │
│  │                                                 │   │
│  │ Por posição:                                    │   │
│  │ INBR32:  -5.2% (sensível a Selic)              │   │
│  │ SUZB3:   +8.1% (beneficia câmbio)              │   │
│  │ BRAV3:   -12.3% (Brent + câmbio)               │   │
│  │ ...                                             │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  ═══════ NEW TRADE ═══════                             │
│                                                        │
│  Simular compra/venda:                                 │
│  ┌────────────────────────────────────────────────┐   │
│  │ Ação: [Comprar ▼]  Ticker: [PLPL3]             │   │
│  │ Quantidade: [500]   Preço: [15.70]              │   │
│  │                                                 │   │
│  │ Impacto:                                        │   │
│  │ Peso PLPL3: 3.4% → 4.9%                        │   │
│  │ Caixa: R$91.798 → R$83.948                      │   │
│  │ Exposição Selic: 45% → 47%                      │   │
│  │ Concentração: HHI 0.XX → 0.XX                   │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

**Funcionalidades:**

1. **Rebalanceamento:**
   - Sliders para ajustar peso-alvo de cada posição
   - Calcula trades necessários (quantidade e valor) para atingir novos pesos
   - Mostra impacto na concentração (HHI) e exposição a fatores

2. **Stress Test:**
   - Sliders para choques em variáveis macro (Selic, câmbio, Brent, IBOV)
   - Calcula impacto estimado no portfólio usando betas/sensibilidades históricas
   - Mostra impacto posição por posição
   - Cenários pré-definidos: "Estagflação", "Risk-off global", "Selic hawkish", "Bull China"

3. **New Trade:**
   - Input: ação (comprar/vender), ticker, quantidade, preço
   - Calcula: novo peso, impacto no caixa, impacto na concentração, impacto na exposição a fatores
   - Não executa — apenas simula

---

### 6.6 Página: Knowledge Base

**Objetivo:** Repositório analítico por ação. Consultar deep dives atuais e históricos, ver evolução das análises ao longo do tempo, buscar por temas.

**Layout:**

```
┌────────────────────────────────────────────────────────┐
│  📚 KNOWLEDGE BASE          [🔍 Buscar] [+ Upload]    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─── NAVEGAÇÃO ───────────────────────────────────┐  │
│  │ [Aba: Por Ticker] [Aba: Relatórios] [Aba: Timeline]│
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ═══════ ABA: POR TICKER ═══════                       │
│                                                        │
│  ┌─── Selecione o Ticker: [INBR32 ▼] ─────────────┐  │
│  │                                                   │  │
│  │  INBR32 — Inter & Co                              │  │
│  │  Deep Dives: 2 versões                            │  │
│  │  Último: 15/02/2026 | Status: 🟢 | Conv: ALTA    │  │
│  │                                                   │  │
│  │  ┌─ EVOLUÇÃO DA ANÁLISE ────────────────────┐    │  │
│  │  │                                           │    │  │
│  │  │  v2 (15/02/2026) ← VIGENTE               │    │  │
│  │  │  Status: 🟢 | Target: R$58 | ROIC: 12%   │    │  │
│  │  │  Mudanças: Atualização pós-Q3 2025...     │    │  │
│  │  │  [📄 Ver completo] [📊 Comparar com v1]  │    │  │
│  │  │                                           │    │  │
│  │  │  v1 (01/02/2026)                          │    │  │
│  │  │  Status: 🟡 | Target: R$52 | ROIC: 10%   │    │  │
│  │  │  [📄 Ver completo]                        │    │  │
│  │  │                                           │    │  │
│  │  └───────────────────────────────────────────┘    │  │
│  │                                                   │  │
│  │  ┌─ MÉTRICAS AO LONGO DO TEMPO ────────────┐    │  │
│  │  │  (Line chart: ROIC, Target Price, Cotação │    │  │
│  │  │   plotados nas datas de cada versão)       │    │  │
│  │  └───────────────────────────────────────────┘    │  │
│  │                                                   │  │
│  │  ┌─ DEEP DIVE VIGENTE (renderizado) ────────┐    │  │
│  │  │  (Markdown renderizado do content_md      │    │  │
│  │  │   da versão mais recente)                 │    │  │
│  │  │  ...                                      │    │  │
│  │  │  [📥 Download .md]                        │    │  │
│  │  └───────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                        │
│  ═══════ ABA: RELATÓRIOS ═══════                       │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │ Filtro: [Tipo ▼] [Tags ▼] [Período ▼]         │   │
│  │                                                 │   │
│  │ 📄 Relatório Macro & Rotação — 12/02/2026      │   │
│  │    Tipo: MACRO | Tags: selic, rotacao           │   │
│  │    Tickers: ENGI4, INBR32, PLPL3...             │   │
│  │    [Ver] [Download]                              │   │
│  │                                                 │   │
│  │ 📄 Oil Analysis — 08/02/2026                    │   │
│  │    Tipo: SECTOR | Tags: oil, brent, brav3       │   │
│  │    Tickers: BRAV3, UGPA3                        │   │
│  │    [Ver] [Download]                              │   │
│  │                                                 │   │
│  │ 📄 Safra 2025/26 — 05/02/2026                  │   │
│  │    Tipo: THEMATIC | Tags: agro, safra           │   │
│  │    [Ver] [Download]                              │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  ═══════ ABA: TIMELINE ═══════                         │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │  TIMELINE DE ANÁLISES (todas as posições)       │   │
│  │                                                 │   │
│  │  Jan 2026 ──── Fev 2026 ──── Mar 2026          │   │
│  │  │              │              │                 │   │
│  │  │ INBR32 v1   │ INBR32 v2   │                 │   │
│  │  │ ENGI4 v1    │ ALOS3 v1    │                 │   │
│  │  │ EQTL3 v1    │ MELI v1     │                 │   │
│  │  │              │ Macro Report│                 │   │
│  │  │              │ Oil Analysis│                 │   │
│  │  │              │             │                 │   │
│  │  │              │             │                 │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

**Funcionalidades:**

1. **Por Ticker (aba principal):**
   - Dropdown para selecionar ticker
   - Lista todas as versões do deep dive (mais recente primeiro)
   - Card resumido por versão: data, status, convicção, target, métricas-chave
   - "Key changes" — o que mudou vs. versão anterior (a partir de v2)
   - Botão "Ver completo" renderiza o Markdown
   - Botão "Comparar com vN" — side-by-side diff de métricas-chave entre versões
   - Gráfico de evolução: ROIC, target price, cotação real plotados nas datas de cada versão
   - Download do .md

2. **Relatórios (aba):**
   - Lista todos os relatórios temáticos (macro, setoriais, etc.)
   - Filtros: tipo, tags, período, tickers mencionados
   - Visualização e download

3. **Timeline (aba):**
   - Plotly timeline mostrando todos os deep dives e relatórios ao longo do tempo
   - Código de cor por tipo (deep dive vs relatório) e por ticker
   - Click para abrir o documento

4. **Busca (header):**
   - Full-text search sobre títulos, summaries, tags e tickers
   - Resultados rankeados por relevância

5. **Upload de novo deep dive:**
   - Formulário para adicionar novo deep dive:
     - Selecionar ticker
     - Upload de arquivo .md OU colar conteúdo Markdown
     - Preencher metadados: status, convicção, target price, métricas-chave
     - Descrever "key changes" vs. versão anterior
     - Auto-calcula: version number, current_price_at_time (via API)
   - Formulário para adicionar relatório temático:
     - Título, tipo, tags, tickers mencionados
     - Upload .md OU colar conteúdo

6. **Comparação entre versões (diff view):**
   - Tabela side-by-side de métricas-chave entre duas versões
   - Highlight de mudanças (verde = melhorou, vermelho = piorou)
   - Exibe os dois textos de "summary" lado a lado

---

### Sprint 1 — MVP Core (Prioridade Máxima)

**Objetivo:** Dashboard funcional com posições reais e cotações atualizadas.

| # | Task | Descrição | Estimativa |
|---|------|-----------|------------|
| 1.1 | Setup projeto | Criar repo, requirements.txt, estrutura de diretórios, .streamlit/config.toml | P |
| 1.2 | Setup Supabase | Criar projeto, tabelas (positions, transactions, theses, catalysts, macro_snapshots, portfolio_snapshots), RLS policies | M |
| 1.3 | Módulo db.py | Conexão Supabase, funções CRUD para todas as tabelas | M |
| 1.4 | Seed data | Script para popular positions e transactions com dados do Excel (seção 4) | P |
| 1.5 | Módulo market_data.py | Fetch de cotações BR (brapi) e US (yfinance), com cache (st.cache_data TTL=15min) | M |
| 1.6 | Módulo macro_data.py | Fetch de indicadores macro (BCB + yfinance), com cache | M |
| 1.7 | Módulo currency.py | Conversão BRL↔USD via PTAX, toggle global | P |
| 1.8 | Módulo portfolio.py | Cálculos: peso atual, P&L, exposição setorial, exposição por fator | M |
| 1.9 | Página Overview | Implementar layout completo da seção 6.1 | G |
| 1.10 | Página Positions | Implementar tabela + detalhes expansíveis (seção 6.2) | G |
| 1.11 | Página Risk & Macro | KPI cards macro + correlation heatmap + risk metrics básicas (seção 6.3) | G |
| 1.12 | Auth básico | Proteção com senha (st.secrets ou Supabase Auth) | P |
| 1.13 | Deploy Streamlit Cloud | Deploy inicial, testar acesso remoto | P |

**P = Pequeno, M = Médio, G = Grande**

### Sprint 2 — Thesis, Catalysts & Knowledge Base

**Objetivo:** Sistema de gestão de teses, catalisadores e repositório analítico.

| # | Task | Descrição |
|---|------|-----------|
| 2.1 | Página Thesis Board | Kanban view (🟢🟡🔴), cards de posição, formulário de edição |
| 2.2 | CRUD Teses | Criar, editar, excluir teses via forms Streamlit → Supabase |
| 2.3 | CRUD Catalisadores | Adicionar/editar/remover catalisadores com data e impacto |
| 2.4 | CRUD Kill Switches | Adicionar/editar/remover kill switches |
| 2.5 | Catalyst Timeline | Plotly timeline dos próximos 90 dias de catalisadores |
| 2.6 | Cálculos auto | Target price (20/60/20), margem de segurança, upside/downside |
| 2.7 | Alertas de revisão | Highlight posições com revisão vencida |
| 2.8 | Integração Overview | Próximos catalisadores no Overview, semáforo de teses na Positions |
| 2.9 | Seed deep dives | Script para ler 18 .md files da pasta knowledge_base/deepdives/ e popular tabela deep_dives |
| 2.10 | Seed relatórios | Script para ler 4 .md files de knowledge_base/reports/ e popular tabela analysis_reports |
| 2.11 | Página Knowledge Base — Aba Por Ticker | Dropdown ticker, lista de versões, renderização Markdown, download |
| 2.12 | Página Knowledge Base — Aba Relatórios | Lista filtrada por tipo/tags, visualização e download |
| 2.13 | Página Knowledge Base — Aba Timeline | Plotly timeline de todos os deep dives e relatórios |
| 2.14 | KB — Upload de novo deep dive | Formulário: selecionar ticker, colar/upload .md, preencher metadados, auto-version |
| 2.15 | KB — Comparação entre versões | Side-by-side de métricas-chave entre versões com highlight de mudanças |
| 2.16 | KB — Gráfico de evolução | Line chart: ROIC, target price, cotação real ao longo das versões do deep dive |
| 2.17 | KB — Busca full-text | Search bar com busca em títulos, summaries, tags, tickers |

### Sprint 3 — Simulator & Advanced Risk

**Objetivo:** Ferramentas de simulação e risk management avançado.

| # | Task | Descrição |
|---|------|-----------|
| 3.1 | Módulo simulator.py | Engine de simulação (rebalanceamento, stress test, new trade) |
| 3.2 | Módulo risk.py | VaR histórico, stress tests, sensitivity analysis |
| 3.3 | Página Simulator | Implementar 3 modos (rebalanceamento, stress test, new trade) |
| 3.4 | Stress scenarios | Cenários pré-definidos (estagflação, risk-off, etc.) |
| 3.5 | Performance attribution | Decomposição: alocação setorial vs. stock picking vs. timing |
| 3.6 | Módulo performance.py | Retornos vs benchmark (IBOV, CDI), Sharpe, Sortino, max drawdown |
| 3.7 | Portfolio snapshots | Job para salvar snapshot diário/semanal do portfólio |
| 3.8 | Drawdown chart | Gráfico de drawdown histórico do portfólio |

### Sprint 4 — Polish & Extras

**Objetivo:** Refinamentos, UX, e funcionalidades complementares.

| # | Task | Descrição |
|---|------|-----------|
| 4.1 | Mobile responsiveness | Testar e ajustar layout para telas menores |
| 4.2 | Export PDF/CSV | Exportar posições e relatórios |
| 4.3 | Registro de transações | Formulário para registrar novas compras/vendas |
| 4.4 | Histórico de P&L | Gráfico de evolução patrimonial ao longo do tempo |
| 4.5 | Tema dark/light | Toggle de tema |
| 4.6 | Celulose manual input | Campo para input manual de preço BHKP |
| 4.7 | Error handling | Tratamento de falhas de API, timeouts, dados faltantes |
| 4.8 | Documentation | README completo, instruções de setup e manutenção |

---

## 8. REQUISITOS NÃO-FUNCIONAIS

| Requisito | Especificação |
|-----------|---------------|
| **Performance** | Página Overview carrega em <5s com dados cacheados, <15s com refresh completo |
| **Disponibilidade** | Streamlit Cloud free tier (pode ter cold starts de ~30s após inatividade) |
| **Segurança** | Autenticação por senha. Dados sensíveis apenas no Supabase (RLS ativo). Sem dados em client-side storage |
| **Responsividade** | Desktop-first. Funcional em mobile (Streamlit wide mode off para mobile) |
| **Cache** | Cotações: TTL 15 min. Macro: TTL 1 hora. Posições DB: TTL 5 min |
| **Backup** | Supabase auto-backup (free tier: diário, 7 dias retenção) |
| **Moeda** | Toggle global BRL/USD. Default: BRL |
| **Idioma** | Interface em Português BR. Termos técnicos em inglês quando consagrados (ROIC, VaR, etc.) |

---

## 9. DADOS DE REFERÊNCIA — CONSTANTES

### 9.1 Benchmarks

```python
BENCHMARKS = {
    "primary": {"name": "IBOV", "ticker": "^BVSP"},
    "hurdle": {"name": "CDI", "series_bcb": 12}
}
```

### 9.2 Setores e Cores

```python
SECTORS = {
    "financeiro": {"label": "Financeiro & Crédito", "color": "#1f77b4"},
    "utilities": {"label": "Utilities & Concessões", "color": "#ff7f0e"},
    "consumo_varejo": {"label": "Consumo, Varejo & Imobiliário", "color": "#2ca02c"},
    "energia_materiais": {"label": "Energia & Materiais Básicos", "color": "#d62728"},
    "tech_semis": {"label": "Tecnologia & Semicondutores", "color": "#9467bd"},
    "fundos": {"label": "Fundos", "color": "#8c564b"},
    "caixa": {"label": "Caixa", "color": "#7f7f7f"}
}
```

### 9.3 Fatores de Risco e Sensibilidades Estimadas

```python
# Sensibilidades aproximadas (beta/elasticidade) para stress tests
# Valores iniciais — devem ser calibrados com dados históricos
FACTOR_SENSITIVITIES = {
    "selic_1pp": {
        # Impacto estimado de +1pp na Selic sobre cada posição
        "INBR32": -0.05, "ENGI4": -0.08, "EQTL3": -0.07,
        "ALOS3": -0.06, "PLPL3": -0.04,
        "SUZB3": -0.02, "KLBN4": -0.02,
        "BRAV3": 0.00, "RAPT4": -0.03, "GMAT3": -0.03,
    },
    "usdbrl_10pct": {
        # Impacto estimado de +10% no USD/BRL
        "SUZB3": +0.08, "KLBN4": +0.06, "BRAV3": +0.05,
        "TSM": -0.10, "NVDA": -0.10, "ASML": -0.10,
        "MELI": -0.10, "GOOGL": -0.10, "SNPS": -0.10, "MU": -0.10,
    },
    "brent_10pct": {
        # Impacto estimado de +10% no Brent
        "BRAV3": +0.12,
        "UGPA3": -0.02,  # margem espremida
    },
    "ibov_10pct": {
        # Beta aproximado vs IBOV
        "INBR32": 1.2, "ENGI4": 0.6, "EQTL3": 0.7,
        "ALOS3": 0.8, "SUZB3": 0.9, "KLBN4": 0.7,
        "BRAV3": 1.3, "PLPL3": 1.1, "RAPT4": 1.0, "GMAT3": 0.8,
    }
}
```

---

## 10. DEPENDÊNCIAS (pyproject.toml)

```toml
[project]
name = "portfolio-cockpit"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "streamlit>=1.30.0",
    "supabase>=2.0.0",
    "plotly>=5.18.0",
    "pandas>=2.1.0",
    "numpy>=1.24.0",
    "yfinance>=0.2.31",
    "requests>=2.31.0",
    "quantstats>=0.0.62",
    "PyPortfolioOpt>=1.5.5",
    "python-bcb>=0.2.0",
    "streamlit-option-menu>=0.3.6",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.4.0",
]

[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Gerenciamento:** `uv` (package manager moderno, substitui pip + venv)
```bash
uv sync          # Instalar/atualizar dependências
uv run <cmd>     # Rodar dentro do venv
```

---

## 11. VARIÁVEIS DE AMBIENTE (.streamlit/secrets.toml)

```toml
# .streamlit/secrets.toml (NÃO commitar — está no .gitignore)
# Copiar de .streamlit/secrets.toml.example e preencher valores

[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJxxxxx..."

[brapi]
token = "xxxxx"

[auth]
password = "xxxxx"
```

**Nota:** Commitar `.streamlit/secrets.toml.example` (sem valores) como template.

---

## 12. CRITÉRIOS DE ACEITE (DEFINITION OF DONE)

### Sprint 1 — MVP Core
- [ ] Dashboard acessível via URL pública com autenticação
- [ ] Página Overview mostra patrimônio total, P&L, alocação setorial, top movers
- [ ] Página Positions mostra todas as 20+ posições com P&L atualizado
- [ ] Posições BR e US com cotações reais (delay max 15min)
- [ ] Toggle BRL/USD funcional em todas as páginas
- [ ] Posições US mostram retorno em USD e em BRL separadamente
- [ ] Macro KPIs atualizados (Selic, câmbio, IBOV, VIX, Brent)
- [ ] Correlation matrix funcional
- [ ] Performance vs IBOV e CDI (gráfico com time range selector)

### Sprint 2 — Thesis, Catalysts & Knowledge Base
- [ ] Kanban de teses (🟢🟡🔴) com cards para cada posição
- [ ] Formulário completo para criar/editar teses (todos os campos da seção 3.3)
- [ ] Catalisadores com CRUD e timeline visual
- [ ] Kill switches editáveis
- [ ] Target price calculado automaticamente (20/60/20)
- [ ] Alertas de revisão vencida visíveis
- [ ] 18 deep dives existentes importados no banco (tabela deep_dives, version=1)
- [ ] 4 relatórios temáticos importados (tabela analysis_reports)
- [ ] Página Knowledge Base — aba "Por Ticker" funcional com dropdown, lista de versões, renderização Markdown
- [ ] Página Knowledge Base — aba "Relatórios" com filtros e visualização
- [ ] Página Knowledge Base — aba "Timeline" com Plotly timeline de todos os documentos
- [ ] Upload de novo deep dive funcional (incrementa versão, extrai metadados)
- [ ] Comparação side-by-side entre versões de deep dive (métricas-chave)
- [ ] Gráfico de evolução por ticker (ROIC, target price, cotação ao longo das versões)
- [ ] Busca full-text sobre títulos, summaries, tags e conteúdo

### Sprint 3 — Simulator
- [ ] Simulação de rebalanceamento com sliders
- [ ] Stress test com 4 variáveis macro
- [ ] Simulação de new trade com impacto calculado
- [ ] Cenários pré-definidos funcionais
- [ ] Drawdown chart e performance attribution

### Sprint 4 — Polish
- [ ] Mobile responsivo (consulta básica funcional)
- [ ] Export CSV/PDF
- [ ] Registro de transações
- [ ] Tema dark/light
- [ ] Error handling robusto (sem crashes em falha de API)
- [ ] README documentado

---

## 13. RISCOS DO PROJETO

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| brapi.dev fora do ar ou mudar API | Cotações BR indisponíveis | Fallback para yfinance com `.SA` |
| Free tier Supabase insuficiente | Dados cortados | 500MB é suficiente para décadas de dados deste portfólio |
| Streamlit Cloud cold starts | Demora 30s para abrir após inatividade | Aceitável para uso semanal |
| yfinance rate limited | Cotações US atrasadas | Cache agressivo (TTL 15min), batch requests |
| Complexidade do Simulator | Atraso na Sprint 3 | Sensibilidades iniciais hardcoded, calibração posterior |

---

## 14. GLOSSÁRIO

| Termo | Definição |
|-------|-----------|
| **GARP** | Growth at Reasonable Price — filosofia de investimento |
| **ROIC** | Return on Invested Capital |
| **WACC** | Weighted Average Cost of Capital |
| **HHI** | Herfindahl-Hirschman Index — medida de concentração |
| **VaR** | Value at Risk — perda máxima estimada com intervalo de confiança |
| **Kill Switch** | Condição pré-definida que, se ocorrer, invalida a tese de investimento |
| **BHKP** | Bleached Hardwood Kraft Pulp — celulose de fibra curta |
| **PTAX** | Taxa de câmbio oficial do Banco Central do Brasil |
| **Seed** | Popular banco de dados com dados iniciais |
| **TTL** | Time To Live — tempo de validade do cache |
| **RLS** | Row Level Security — política de segurança do Supabase |

---

*Documento gerado pelo CIO do Comitê de Investimentos em 18/02/2026.*
*Para execução via Claude Code em minitasks sequenciais.*