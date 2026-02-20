# Portfolio Cockpit

Dashboard de monitoramento de portfólio de investimentos para family office, construído com Streamlit.

## Stack

- **Frontend/UI:** Streamlit + Plotly
- **Banco de dados:** Supabase (PostgreSQL)
- **Dados de mercado:** brapi.dev (BR) + yfinance (US)
- **Dados macro:** BCB API + yfinance
- **Analytics:** Pandas, NumPy
- **Deploy:** Streamlit Cloud

## Setup

### Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Conta Supabase (free tier)
- Token brapi.dev (gratuito)

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
uv run pytest tests/ -x          # Testes
```

## Estrutura

```
portfolio-cockpit/
├── app.py                  # Entry point (multipage + auth)
├── pages/                  # 6 páginas do dashboard
│   ├── 1_overview.py       # Visão geral, KPIs, alocação
│   ├── 2_positions.py      # Detalhes de cada posição
│   ├── 3_risk_macro.py     # Indicadores macro e risco
│   ├── 4_thesis_board.py   # Gestão de teses de investimento
│   ├── 5_knowledge_base.py # Repositório de deep dives
│   └── 6_simulator.py      # Simulação what-if
├── data/                   # Camada de dados
│   ├── db.py               # CRUD Supabase
│   ├── market_data.py      # Cotações BR/US
│   ├── macro_data.py       # Indicadores macro
│   └── seed.py             # Popular banco inicial
├── analytics/              # Cálculos
│   ├── portfolio.py        # Pesos, P&L, exposição
│   ├── performance.py      # Sharpe, Sortino, drawdown
│   ├── risk.py             # VaR, stress tests
│   └── simulator.py        # Engine de simulação
├── utils/                  # Helpers
│   ├── constants.py        # Tickers, setores, configs
│   ├── formatting.py       # Formatação de moedas/datas
│   └── currency.py         # Conversão BRL/USD
└── tests/                  # Testes (analytics/)
```

## Páginas

| Página | Funcionalidade |
|--------|---------------|
| **Overview** | KPIs, alocação setorial, top movers, exposição por fator, catalisadores |
| **Positions** | Tabela de posições, P&L, detalhes, registro de transações, export CSV |
| **Risk & Macro** | Indicadores macro, stress matrix, correlation matrix, risk metrics, drawdown |
| **Thesis Board** | Kanban de teses (verde/amarelo/vermelho), CRUD, catalisadores, timeline |
| **Knowledge Base** | Deep dives por ticker, relatórios, comparação entre versões, timeline |
| **Simulator** | Rebalanceamento, stress test (4 cenários), simulação de trade |

## Testes

Testes cobrem apenas os módulos em `analytics/`:

```bash
uv run pytest tests/ -x -v
```

## Deploy

O app é deployado no [Streamlit Cloud](https://streamlit.io/cloud). As secrets são configuradas diretamente na interface do Streamlit Cloud.
