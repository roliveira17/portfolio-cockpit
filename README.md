# Portfolio Cockpit

Dashboard de monitoramento de portfólio de investimentos para family office, construído com Streamlit.

## Stack

- **Frontend/UI:** Streamlit + Plotly
- **Banco de dados:** Supabase (PostgreSQL)
- **Dados de mercado:** brapi.dev (BR) + yfinance (US)
- **Dados macro:** BCB API + yfinance
- **Curva de juros:** pyettj (BR DI x Pré) + Treasury.gov XML (US)
- **Chat/LLM:** OpenRouter (9 modelos via SDK OpenAI)
- **Analytics:** Pandas, NumPy
- **Deploy:** Streamlit Cloud

## Setup

### Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Conta Supabase (free tier)
- Token brapi.dev (gratuito)
- API key OpenRouter (para Chat Assessor)

### Instalação

```bash
git clone https://github.com/roliveira17/portfolio-cockpit.git
cd portfolio-cockpit
uv sync
```

### Configuração

Copiar o template de secrets e preencher os valores:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Editar `.streamlit/secrets.toml` com:

```toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJxxxxx..."

[brapi]
token = "xxxxx"

[auth]
password = "xxxxx"

[openrouter]
api_key = "sk-or-xxxxx"
```

### Banco de dados

Criar as tabelas no Supabase usando as migrations em `supabase/migrations/`. Popular com dados iniciais:

```bash
uv run python -m data.seed
```

### Rodar localmente

```bash
uv run streamlit run app.py
```

## Comandos

```bash
uv sync                          # Instalar dependências
uv run streamlit run app.py      # Rodar local
uv run ruff check .              # Lint
uv run ruff format .             # Formatar
uv run pytest tests/ -x          # Testes (321 testes, ~1.7s)
```

## Estrutura

```
portfolio-cockpit/
├── app.py                  # Entry point (multipage + auth)
├── pages/                  # 7 páginas do dashboard
│   ├── 1_overview.py       # Visão geral, KPIs, alocação
│   ├── 2_positions.py      # Detalhes de cada posição
│   ├── 3_risk_macro.py     # Indicadores macro e risco
│   ├── 4_chat.py           # Chat Assessor (análise via LLM)
│   ├── 5_knowledge_base.py # Repositório de deep dives
│   ├── 6_simulator.py      # Simulação what-if
│   └── 7_markets.py        # Índices globais, commodities, curva de juros
├── data/                   # Camada de dados
│   ├── db.py               # CRUD Supabase
│   ├── market_data.py      # Cotações BR/US
│   ├── macro_data.py       # Indicadores macro
│   ├── llm.py              # Cliente OpenRouter
│   ├── chat_prompts.py     # Prompts e contexto do Chat
│   ├── yield_curve.py      # Curva DI x Pré + Treasury
│   ├── global_markets.py   # Índices globais + commodities
│   └── seed.py             # Popular banco inicial
├── analytics/              # Cálculos
│   ├── portfolio.py        # Pesos, P&L, exposição
│   ├── performance.py      # Sharpe, Sortino, drawdown
│   ├── risk.py             # VaR, stress tests
│   └── simulator.py        # Engine de simulação
├── utils/                  # Helpers
│   ├── constants.py        # Tickers, setores, configs
│   ├── formatting.py       # Formatação de moedas/datas
│   ├── currency.py         # Conversão BRL/USD
│   └── cache_info.py       # Freshness badges
└── tests/                  # 321 testes (utils/, data/, analytics/)
```

## Páginas

| Página | Funcionalidade |
|--------|---------------|
| **Overview** | KPIs, alocação setorial, top movers, exposição por fator, catalisadores |
| **Positions** | Tabela de posições, P&L, sparklines, registro de transações, import/export CSV |
| **Risk & Macro** | Indicadores macro, curva DI, stress matrix, correlation matrix, risk metrics, drawdown |
| **Chat Assessor** | Análise de posições via LLM (OpenRouter), gestão de teses por conversa, vision |
| **Knowledge Base** | Deep dives por ticker, relatórios, comparação entre versões, busca full-text |
| **Simulator** | Rebalanceamento, stress test (4 cenários macro), simulação de trade |
| **Markets** | Índices globais por região, commodities, curva de juros BR + US side-by-side |

## Testes

321 testes cobrindo `utils/`, `data/` e `analytics/` (100% mockados, sem I/O real):

```bash
uv run pytest tests/ -x -v
```

## Deploy

O app é deployado no [Streamlit Cloud](https://streamlit.io/cloud). As secrets são configuradas diretamente na interface do Streamlit Cloud.
