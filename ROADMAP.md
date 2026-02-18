# ROADMAP — Portfolio Cockpit

> Última atualização: 2026-02-18 (sessão 1)
> Spec completa: docs/specs/PRD.md

---

## Sprint 1 — MVP Core

### Setup & Infraestrutura
- [x] ✅ 2026/02/18 1.1 Setup projeto (repo, pyproject.toml, estrutura de diretórios, .streamlit/config.toml, .gitignore)
- [ ] 1.2 Setup Supabase (criar projeto, tabelas, RLS policies)
- [ ] 1.3 Módulo `data/db.py` (conexão Supabase, funções CRUD)
- [ ] 1.4 Seed data (popular positions e transactions com dados do PRD seção 4)

### Utils (dependências dos módulos de data)
- [ ] 1.5 Módulo `utils/constants.py` (tickers, setores, benchmarks, cores)
- [ ] 1.6 Módulo `utils/formatting.py` (formatação de moedas, %, datas)

### Data Layer
- [ ] 1.7 Módulo `data/market_data.py` (cotações BR via brapi + US via yfinance, com cache)
- [ ] 1.8 Módulo `data/macro_data.py` (indicadores macro BCB + yfinance, com cache)
- [ ] 1.9 Módulo `utils/currency.py` (conversão BRL↔USD via PTAX)

### Analytics
- [ ] 1.10 Módulo `analytics/portfolio.py` (peso atual, P&L, exposição setorial, exposição por fator)

### Páginas
- [ ] 1.11 Entry point `app.py` (config multipage, sidebar)
- [ ] 1.12 Auth básico (proteção com senha via st.secrets)
- [ ] 1.13 Página Overview (layout completo: KPIs, donut, top movers, performance chart, fatores)
- [ ] 1.14 Página Positions (tabela sortável, filtros, detalhes expansíveis, P&L)
- [ ] 1.15 Página Risk & Macro — aba Macro (KPI cards macro, curva de juros)
- [ ] 1.16 Página Risk & Macro — aba Risk (correlation heatmap, HHI, risk metrics)

### Deploy
- [ ] 1.17 Deploy Streamlit Cloud (testar acesso remoto + auth)

---

## Sprint 2 — Thesis, Catalysts & Knowledge Base

### Thesis Board
- [ ] 2.1 Página Thesis Board (kanban 🟢🟡🔴, cards, formulário edição)
- [ ] 2.2 CRUD Teses (criar/editar/excluir via Streamlit → Supabase)
- [ ] 2.3 CRUD Catalisadores (adicionar/editar/remover com data e impacto)
- [ ] 2.4 CRUD Kill Switches
- [ ] 2.5 Catalyst Timeline (Plotly timeline próximos 90 dias)
- [ ] 2.6 Cálculos automáticos (target price 20/60/20, margem de segurança)
- [ ] 2.7 Alertas de revisão vencida
- [ ] 2.8 Integração Overview (catalisadores + semáforo de teses)

### Knowledge Base
- [ ] 2.9 Seed deep dives (ler 18 .md de knowledge_base/deepdives/ → tabela deep_dives)
- [ ] 2.10 Seed relatórios (ler 4 .md de knowledge_base/reports/ → tabela analysis_reports)
- [ ] 2.11 Página KB — aba Por Ticker (dropdown, versões, render Markdown, download)
- [ ] 2.12 Página KB — aba Relatórios (lista filtrada, visualização, download)
- [ ] 2.13 Página KB — aba Timeline (Plotly timeline de todos os documentos)
- [ ] 2.14 KB — Upload de novo deep dive (formulário, auto-version)
- [ ] 2.15 KB — Comparação entre versões (side-by-side de métricas)
- [ ] 2.16 KB — Gráfico de evolução por ticker (ROIC, target, cotação ao longo das versões)
- [ ] 2.17 KB — Busca full-text

---

## Sprint 3 — Simulator & Advanced Risk

- [ ] 3.1 Módulo `analytics/simulator.py`
- [ ] 3.2 Módulo `analytics/risk.py` (VaR, stress tests, sensitivity)
- [ ] 3.3 Página Simulator — modo Rebalanceamento
- [ ] 3.4 Página Simulator — modo Stress Test
- [ ] 3.5 Página Simulator — modo New Trade
- [ ] 3.6 Cenários pré-definidos (estagflação, risk-off, etc.)
- [ ] 3.7 Módulo `analytics/performance.py` (attribution, Sharpe, Sortino)
- [ ] 3.8 Portfolio snapshots (job periódico)
- [ ] 3.9 Drawdown chart

---

## Sprint 4 — Polish & Extras

- [ ] 4.1 Mobile responsiveness
- [ ] 4.2 Export PDF/CSV
- [ ] 4.3 Registro de transações (formulário)
- [ ] 4.4 Histórico de evolução patrimonial
- [ ] 4.5 Tema dark/light
- [ ] 4.6 Celulose BHKP input manual
- [ ] 4.7 Error handling robusto
- [ ] 4.8 README e documentação final

---

## Notas

- Spec completa com wireframes, modelo de dados e APIs: `docs/specs/PRD.md`
- Framework de análise do portfólio: `knowledge_base/frameworks/framework_analise.md`
- Deep dives existentes (18 arquivos): `knowledge_base/deepdives/`