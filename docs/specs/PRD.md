# PRD — PORTFOLIO COCKPIT (Referência Compacta)

> **Versão:** 2.0 (compactado)
> **Original:** v1.0 — 18/02/2026 — CIO do Comitê de Investimentos
> **Compactação:** 22/02/2026 — Projeto completo (Sprints 1-9 finalizados)

---

## 1. PRINCÍPIOS DE DESIGN

1. **Profundidade analítica > Estética superficial.** Informação acionável sobre decoração.
2. **GARP-centric.** Métricas servem à filosofia Quality + Growth.
3. **Dados reais, não mock.** APIs de mercado reais desde o MVP.
4. **Simulação como ferramenta central.** Testar cenários ("e se eu vender 50% de X?").
5. **Teses vivas.** Sistema de gestão de convicção, não só P&L.

---

## 2. PÁGINAS DO DASHBOARD

| # | Arquivo | Objetivo |
|---|---------|----------|
| 1 | `1_overview.py` | Visão de helicóptero: KPIs, alocação setorial, top movers, performance vs benchmarks, catalisadores |
| 2 | `2_positions.py` | Tabela detalhada de posições com P&L, pesos, filtros, cenários de valuation |
| 3 | `3_risk_macro.py` | Macro KPIs (Selic, câmbio, IBOV, VIX, Brent), correlation heatmap, HHI, risk metrics, curva DI, stress matrix |
| 4 | `4_chat.py` | Chat Assessor — análise de posições via LLM (OpenRouter), gestão de teses por conversa |
| 5 | `5_knowledge_base.py` | Repositório de deep dives e relatórios, busca, upload, versionamento por ticker |
| 6 | `6_simulator.py` | Rebalanceamento, stress test (4 variáveis macro), simulação de new trade |
| 7 | `7_markets.py` | Cotações em tempo real, gráficos intraday, comparativos de mercado |

---

## 3. MODELO DE DADOS (SUPABASE)

### 3.1 `positions`
- `id` uuid PK, `ticker` text, `company_name` text, `market` text (BR/US), `currency` text (BRL/USD)
- `sector` text (energia_materiais, utilities, consumo_varejo, tech_semis, financeiro, fundos, caixa)
- `analyst` text, `quantity` decimal, `avg_price` decimal, `total_invested` decimal
- `dividends_received` decimal, `target_weight` decimal, `is_active` boolean
- `created_at` timestamp, `updated_at` timestamp

### 3.2 `transactions`
- `id` uuid PK, `position_id` uuid FK, `ticker` text, `type` text (BUY/SELL/DIVIDEND)
- `quantity` decimal, `price` decimal, `total_value` decimal, `currency` text
- `date` date, `notes` text, `created_at` timestamp

### 3.3 `theses`
- `id` uuid PK, `position_id` uuid FK, `ticker` text
- `status` text (GREEN/YELLOW/RED), `conviction` text (HIGH/MEDIUM/LOW)
- `summary` text, `moat_rating` text (STRONG/MODERATE/WEAK/NONE), `moat_trend` text (WIDENING/STABLE/NARROWING)
- `growth_drivers` jsonb, `bull_case_price` decimal, `base_case_price` decimal, `bear_case_price` decimal
- `target_price` decimal (= Bull*20% + Base*60% + Bear*20%)
- `kill_switches` jsonb, `catalysts` jsonb, `key_risks` jsonb
- `roic_current` decimal, `wacc_estimated` decimal
- `last_review` date, `next_review` date, `review_trigger` text, `notes` text
- `created_at` timestamp, `updated_at` timestamp

### 3.4 `catalysts`
- `id` uuid PK, `ticker` text, `description` text, `expected_date` date
- `impact` text (HIGH/MEDIUM/LOW), `category` text (EARNINGS/REGULATORY/MACRO/CORPORATE/OTHER)
- `completed` boolean, `outcome_notes` text, `created_at` timestamp

### 3.5 `macro_snapshots`
- `id` uuid PK, `date` date
- `selic` decimal, `ipca_12m` decimal, `usd_brl` decimal, `dxy` decimal
- `ibov` decimal, `sp500` decimal, `vix` decimal, `brent` decimal
- `cellulose_bhkp` decimal, `treasury_10y` decimal, `di_jan27` decimal, `cds_brazil_5y` decimal
- `created_at` timestamp

### 3.6 `deep_dives`
- `id` uuid PK, `ticker` text, `version` integer (auto-increment por ticker), `title` text, `analyst` text
- `content_md` text, `summary` text
- `thesis_status_at_time` text, `conviction_at_time` text, `target_price_at_time` decimal, `current_price_at_time` decimal
- `key_metrics` jsonb, `key_changes` text, `tags` text[], `date` date, `created_at` timestamp

### 3.7 `analysis_reports`
- `id` uuid PK, `title` text, `report_type` text (MACRO/SECTOR/THEMATIC/PORTFOLIO_REVIEW)
- `content_md` text, `summary` text, `tickers_mentioned` text[], `tags` text[]
- `date` date, `created_at` timestamp

### 3.8 `portfolio_snapshots`
- `id` uuid PK, `date` date
- `total_value_brl` decimal, `total_value_usd` decimal, `cash_brl` decimal
- `positions_data` jsonb, `ibov_value` decimal, `cdi_accumulated` decimal
- `created_at` timestamp

---

## 4. APIs — REFERÊNCIA RÁPIDA

### Cotações BR — brapi.dev
`GET https://brapi.dev/api/quote/{tickers}` (token obrigatório, 15 req/min free tier)
Fallback: yfinance com `.SA`

### Cotações US — yfinance
`yf.download(["TSM","NVDA","ASML","MELI","GOOGL","SNPS","MU"])` — cache agressivo

### Macro Brasil — BCB SGS
| Indicador | Série | Freq |
|-----------|-------|------|
| Selic Meta | 432 | Diária |
| IPCA mensal | 433 | Mensal |
| IPCA 12m | 13522 | Mensal |
| CDI acum. | 12 | Diária |
| PTAX | 1 | Diária |

### Macro Global — yfinance
| Indicador | Ticker |
|-----------|--------|
| S&P 500 | ^GSPC |
| VIX | ^VIX |
| DXY | DX-Y.NYB |
| Brent | BZ=F |
| Treasury 10Y | ^TNX |
| Ibovespa | ^BVSP |

---

## 5. REQUISITOS NÃO-FUNCIONAIS

| Requisito | Especificação |
|-----------|---------------|
| **Performance** | Overview <5s cacheado, <15s refresh completo |
| **Cache** | Cotações: TTL 15min. Macro: TTL 1h. Posições DB: TTL 5min |
| **Segurança** | Auth por senha. RLS ativo no Supabase |
| **Moeda** | Toggle global BRL/USD. Default: BRL |
| **Idioma** | Interface PT-BR. Termos técnicos em inglês (ROIC, VaR, etc.) |

---

## 6. MAPEAMENTO SETOR → ANALISTA

| Setor | Analista | Tickers |
|-------|----------|---------|
| energia_materiais | Energia & Materiais | BRAV3, SUZB3, KLBN4, UGPA3 |
| utilities | Utilities & Concessões | ENGI4, EQTL3 |
| consumo_varejo | Consumo, Varejo & Imobiliário | GMAT3, ALOS3, PLPL3, RAPT4 |
| tech_semis | Tecnologia & Semicondutores | TSM, NVDA, ASML, MELI, GOOGL, SNPS, MU |
| financeiro | Financeiro & Crédito | INBR32 |

---

## 7. GLOSSÁRIO

| Termo | Definição |
|-------|-----------|
| **GARP** | Growth at Reasonable Price — filosofia de investimento |
| **ROIC** | Return on Invested Capital |
| **WACC** | Weighted Average Cost of Capital |
| **HHI** | Herfindahl-Hirschman Index — concentração (<0.10 diversificado, >0.18 concentrado) |
| **VaR** | Value at Risk — perda máxima estimada com intervalo de confiança |
| **Kill Switch** | Condição que invalida a tese de investimento |
| **BHKP** | Bleached Hardwood Kraft Pulp — celulose de fibra curta |
| **PTAX** | Taxa de câmbio oficial do BCB |

---

**Nota:** Constantes (setores, cores, sensibilidades, benchmarks) vivem em `utils/constants.py` (source of truth).
Dependências vivem em `pyproject.toml` + `requirements.txt`. Secrets template em `.streamlit/secrets.toml.example`.
