# ROADMAP — Portfolio Cockpit

> Última atualização: 2026-02-21 (sessão 7 — QA)
> Spec completa: docs/specs/PRD.md

---

## Sprint 1 — MVP Core

### Setup & Infraestrutura
- [x] ✅ 2026/02/18 1.1 Setup projeto (repo, pyproject.toml, estrutura de diretórios, .streamlit/config.toml, .gitignore)
- [x] ✅ 2026/02/18 1.2 Setup Supabase (criar projeto, tabelas, RLS policies)
- [x] ✅ 2026/02/18 1.3 Módulo `data/db.py` (conexão Supabase, funções CRUD)
- [x] ✅ 2026/02/18 1.4 Seed data (popular positions e transactions com dados do PRD seção 4)

### Utils (dependências dos módulos de data)
- [x] ✅ 2026/02/18 1.5 Módulo `utils/constants.py` (tickers, setores, benchmarks, cores)
- [x] ✅ 2026/02/18 1.6 Módulo `utils/formatting.py` (formatação de moedas, %, datas)

### Data Layer
- [x] ✅ 2026/02/18 1.7 Módulo `data/market_data.py` (cotações BR via brapi + US via yfinance, com cache)
- [x] ✅ 2026/02/18 1.8 Módulo `data/macro_data.py` (indicadores macro BCB + yfinance, com cache)
- [x] ✅ 2026/02/18 1.9 Módulo `utils/currency.py` (conversão BRL↔USD via PTAX)

### Analytics
- [x] ✅ 2026/02/18 1.10 Módulo `analytics/portfolio.py` (peso atual, P&L, exposição setorial, exposição por fator)

### Páginas
- [x] ✅ 2026/02/18 1.11 Entry point `app.py` (config multipage, sidebar)
- [x] ✅ 2026/02/18 1.12 Auth básico (proteção com senha via st.secrets)
- [x] ✅ 2026/02/18 1.13 Página Overview (KPIs, donut, top movers, exposição por fator, catalisadores)
- [x] ✅ 2026/02/18 1.14 Página Positions (tabela sortável, filtros, detalhes expansíveis, P&L, export CSV)
- [x] ✅ 2026/02/18 1.15 Página Risk & Macro — aba Macro (KPI cards macro, matriz impacto)
- [x] ✅ 2026/02/18 1.16 Página Risk & Macro — aba Risk (correlation heatmap, HHI, diversificação)

### Deploy
- [x] ✅ 2026/02/19 1.17 Deploy Streamlit Cloud (testar acesso remoto + auth)

---

## Sprint 2 — Thesis, Catalysts & Knowledge Base

### Thesis Board
- [x] ✅ 2026/02/19 2.1 Página Thesis Board (kanban 🟢🟡🔴, cards, formulário edição)
- [x] ✅ 2026/02/19 2.2 CRUD Teses (criar/editar/excluir via Streamlit → Supabase)
- [x] ✅ 2026/02/19 2.3 CRUD Catalisadores (adicionar/editar/remover com data e impacto)
- [x] ✅ 2026/02/19 2.4 CRUD Kill Switches
- [x] ✅ 2026/02/19 2.5 Catalyst Timeline (Plotly timeline próximos 90 dias)
- [x] ✅ 2026/02/19 2.6 Cálculos automáticos (target price 20/60/20, margem de segurança)
- [x] ✅ 2026/02/19 2.7 Alertas de revisão vencida
- [x] ✅ 2026/02/19 2.8 Integração Overview (catalisadores + semáforo de teses)

### Knowledge Base
- [x] ✅ 2026/02/19 2.9 Seed deep dives (ler 18 .md de knowledge_base/deepdives/ → tabela deep_dives)
- [x] ✅ 2026/02/19 2.10 Seed relatórios (ler 4 .md de knowledge_base/reports/ → tabela analysis_reports)
- [x] ✅ 2026/02/19 2.11 Página KB — aba Por Ticker (dropdown, versões, render Markdown, download)
- [x] ✅ 2026/02/19 2.12 Página KB — aba Relatórios (lista filtrada, visualização, download)
- [x] ✅ 2026/02/19 2.13 Página KB — aba Timeline (Plotly timeline de todos os documentos)
- [x] ✅ 2026/02/19 2.14 KB — Upload de novo deep dive (formulário, auto-version)
- [x] ✅ 2026/02/19 2.15 KB — Comparação entre versões (side-by-side de métricas)
- [x] ✅ 2026/02/19 2.16 KB — Gráfico de evolução por ticker (ROIC, target, cotação ao longo das versões)
- [x] ✅ 2026/02/19 2.17 KB — Busca full-text

---

## Sprint 3 — Simulator & Advanced Risk

- [x] ✅ 2026/02/19 3.1 Módulo `analytics/simulator.py` (rebalance, new trade, HHI)
- [x] ✅ 2026/02/19 3.2 Módulo `analytics/risk.py` (VaR histórico, stress tests, 4 cenários)
- [x] ✅ 2026/02/19 3.3 Página Simulator — modo Rebalanceamento (sliders de peso)
- [x] ✅ 2026/02/19 3.4 Página Simulator — modo Stress Test (4 sliders + cenários)
- [x] ✅ 2026/02/19 3.5 Página Simulator — modo New Trade (impacto peso/caixa/HHI)
- [x] ✅ 2026/02/19 3.6 Cenários pré-definidos (Estagflação, Risk-off, Selic Hawkish, Bull China)
- [x] ✅ 2026/02/19 3.7 Módulo `analytics/performance.py` (Sharpe, Sortino, drawdown, beta, volatilidade)
- [x] ✅ 2026/02/19 3.8 Portfolio snapshots (auto-save diário no Overview)
- [x] ✅ 2026/02/19 3.9 Drawdown chart + upgrade Risk & Macro com métricas reais

---

## Sprint 4 — Polish & Extras

- [x] ✅ 2026/02/19 4.1 Mobile responsiveness (expanders para seções densas)
- [x] ✅ 2026/02/19 4.2 Export CSV (Positions + Simulator stress test)
- [x] ✅ 2026/02/19 4.3 Registro de transações (formulário BUY/SELL/DIVIDEND)
- [x] ✅ 2026/02/19 4.4 Histórico de evolução patrimonial (line chart de snapshots)
- [ ] 4.5 Tema dark/light — DEPRIORITIZADO (Streamlit não suporta toggle runtime)
- [x] ✅ 2026/02/19 4.6 Celulose BHKP input manual (number_input no Risk & Macro)
- [x] ✅ 2026/02/19 4.7 Error handling robusto (try/except em DB, st.warning graciosos)
- [x] ✅ 2026/02/19 4.8 README e documentação final

---

## Sprint 5 — Chat Assessor & KB Refactor (v2.0)

### Infraestrutura
- [x] ✅ 2026/02/20 5.1 Dependências e configuração (openai, OpenRouter, OPENROUTER_MODELS)
- [x] ✅ 2026/02/20 5.2 Módulo `data/llm.py` (cliente OpenRouter, streaming, vision, extração JSON)
- [x] ✅ 2026/02/20 5.3 Módulo `data/chat_prompts.py` (system prompt, contexto dinâmico, detecção de intent)

### Fix & Seed
- [x] ✅ 2026/02/20 5.4 Estender `data/seed.py` para popular tabela `theses` + fix encoding mojibake
- [x] ✅ 2026/02/20 5.5 Novos helpers em `data/db.py` (upsert_thesis, update_position_fields, summaries)

### Chat Assessor (substitui Thesis Board)
- [x] ✅ 2026/02/20 5.6 Página `pages/4_chat.py` (UI principal, modelo selector, sidebar kanban)
- [x] ✅ 2026/02/20 5.7 Fluxo "salvar" no chat (extração JSON + persistência em theses/deep_dives)
- [x] ✅ 2026/02/20 5.8 Atualização de posições via chat (texto, copy-paste, screenshot, vision)

### Knowledge Base Refatorada
- [x] ✅ 2026/02/20 5.9 Refatorar KB para layout de cards (remover tabs, timeline, upload form)
- [x] ✅ 2026/02/20 5.10 Filtros na KB (busca, ticker, tipo, status, setor, conviction, período)
- [x] ✅ 2026/02/20 5.11 Manter comparação entre versões no KB (botão por card)

### Integração
- [x] ✅ 2026/02/20 5.12 Atualizar `app.py` (Thesis Board → Assessor)
- [x] ✅ 2026/02/20 5.13 Atualizar ROADMAP.md
- [x] ✅ 2026/02/20 5.14 Verificação (lint, testes)

---

## Sprint 6 — Market Monitor & UX Enhancements

> Inspiração: Bloomberg Terminal clone adaptado ao stack Streamlit.
> Novas fontes: pyettj (curva BR), Treasury.gov XML (curva US), yfinance (índices/commodities).

### Infraestrutura & Dados
- [x] ✅ 2026/02/21 6.1 Adicionar dependências (`pyettj`, `beautifulsoup4`, `lxml`)
- [x] ✅ 2026/02/21 6.2 Criar `data/yield_curve.py` (curva DI x Pré via pyettj/B3, Treasury yields via XML feed)
- [x] ✅ 2026/02/21 6.3 Criar `data/global_markets.py` (índices globais + commodities via yfinance)
- [x] ✅ 2026/02/21 6.4 Expandir `utils/constants.py` (GLOBAL_INDICES, COMMODITIES_TICKERS, REGION_LABELS, TREASURY_MATURITIES)

### Nova Página: Markets
- [x] ✅ 2026/02/21 6.5 Criar `pages/7_markets.py` — aba Índices Globais (tabela por região, KPIs)
- [x] ✅ 2026/02/21 6.6 Página Markets — aba Commodities (tabela, KPIs, input BHKP migrado)
- [x] ✅ 2026/02/21 6.7 Página Markets — aba Curva de Juros (BR DI x Pré + US Treasury side-by-side)

### UX Enhancements
- [x] ✅ 2026/02/21 6.8 Indicador de freshness dos dados (`utils/cache_info.py` + badge nas páginas)
- [x] ✅ 2026/02/21 6.9 Sparklines na tabela Positions (LineChartColumn nativo do Streamlit)
- [x] ✅ 2026/02/21 6.10 Filtros rápidos preset na Positions (Overweight, Underweight, Top P&L, Revisão Vencida)
- [x] ✅ 2026/02/21 6.11 Botão "Analisar" por posição (análise IA rápida via LLM existente)

### Integração & Testes
- [x] ✅ 2026/02/21 6.12 Registrar página Markets no `app.py`
- [x] ✅ 2026/02/21 6.13 Testes (`tests/test_markets.py` — 11 testes: parse XML, estrutura de constantes, cache_info)
- [x] ✅ 2026/02/21 6.14 Atualizar ROADMAP.md e verificação (lint, testes, deploy)

---

## Sprint 7 — QA Test Automation

> Expandir cobertura de testes de 49 para 311 testes cobrindo todas as camadas.

### Pure Functions (Equipe A)
- [x] ✅ 2026/02/21 7.1 `tests/test_formatting.py` (40 testes — fmt_brl, fmt_usd, fmt_pct, fmt_number, fmt_date, fmt_delta)
- [x] ✅ 2026/02/21 7.2 `tests/test_currency.py` (11 testes — get_ptax, brl_to_usd, usd_to_brl, roundtrip)
- [x] ✅ 2026/02/21 7.3 `tests/test_seed_extraction.py` (55 testes — 15 funções de extração puras do seed.py)
- [x] ✅ 2026/02/21 7.4 `tests/test_chat_prompts.py` (32 testes — prompts, contexto, detecção de intent)
- [x] ✅ 2026/02/21 7.5 `tests/test_portfolio_extended.py` (18 testes — build_portfolio_df, patrimônio, P&L, setor, fator, movers)

### API Mocks (Equipe B)
- [x] ✅ 2026/02/21 7.6 `tests/test_market_data.py` (17 testes — brapi, yfinance, yfinance_br, fetch_all_quotes)
- [x] ✅ 2026/02/21 7.7 `tests/test_macro_data.py` (10 testes — BCB, yfinance macro, fetch_macro_snapshot)
- [x] ✅ 2026/02/21 7.8 `tests/test_yield_curve.py` (9 testes — pyettj BR, Treasury XML US)
- [x] ✅ 2026/02/21 7.9 `tests/test_global_markets.py` (5 testes — índices globais, commodities)
- [x] ✅ 2026/02/21 7.10 `tests/test_llm.py` (14 testes — OpenRouter client, parse JSON, vision)

### DB Mocks (Equipe C)
- [x] ✅ 2026/02/21 7.11 `tests/test_db.py` (51 testes — 20+ funções CRUD Supabase com chainable mocks)

### Verificação
- [x] ✅ 2026/02/21 7.12 Atualizar `tests/conftest.py` com fixtures compartilhadas (brapi, treasury XML, supabase, positions, quotes)
- [x] ✅ 2026/02/21 7.13 311 testes passando em ~1.6s, ruff lint limpo

---

## Pendente — Ações Manuais (pós-deploy)

- [x] ✅ 2026/02/21 Adicionar API key OpenRouter nos secrets do Streamlit Cloud (`[openrouter] api_key`)
- [x] ✅ 2026/02/21 Rodar seed de teses: `uv run python -m data.seed`
- [x] ✅ 2026/02/21 Deletar arquivo morto `pages/4_thesis_board.py`
- [ ] Teste manual: chat (streaming, vision), salvar análise, atualizar posição, KB filtros
- [x] ✅ 2026/02/21 `requirements.txt` já contém todas as dependências (pyettj, beautifulsoup4, lxml)

---

## Notas

- Spec completa com wireframes, modelo de dados e APIs: `docs/specs/PRD.md`
- Framework de análise do portfólio: `knowledge_base/frameworks/framework_analise.md`
- Deep dives existentes (18 arquivos): `knowledge_base/deepdives/`
- Chat usa OpenRouter como gateway (9 modelos disponíveis)
- Antigo `pages/4_thesis_board.py` substituído por `pages/4_chat.py`