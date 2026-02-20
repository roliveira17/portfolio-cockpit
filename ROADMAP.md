# ROADMAP — Portfolio Cockpit

> Última atualização: 2026-02-19 (sessão 4)
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

## Notas

- Spec completa com wireframes, modelo de dados e APIs: `docs/specs/PRD.md`
- Framework de análise do portfólio: `knowledge_base/frameworks/framework_analise.md`
- Deep dives existentes (18 arquivos): `knowledge_base/deepdives/`