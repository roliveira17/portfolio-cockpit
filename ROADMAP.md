# ROADMAP — Portfolio Cockpit

> Última atualização: 2026-02-22
> Spec: docs/specs/PRD.md

---

## Sprints Concluídos

| Sprint | Data | Escopo | Itens |
|--------|------|--------|-------|
| 1 — MVP Core | 2026/02/18-19 | Setup, Supabase, db.py, seed, market_data, macro_data, currency, portfolio.py, app.py, auth, Overview, Positions, Risk & Macro, deploy | 17 |
| 2 — Thesis & KB | 2026/02/19 | Thesis Board (kanban, CRUD teses/catalisadores/kill switches, timeline), KB (seed 18 deep dives + 4 relatórios, aba ticker/relatórios/timeline, upload, comparação, busca) | 17 |
| 3 — Simulator & Risk | 2026/02/19 | simulator.py, risk.py (VaR, stress tests, 4 cenários), performance.py (Sharpe, Sortino, drawdown), Simulator page (3 modos), portfolio snapshots | 9 |
| 4 — Polish | 2026/02/19 | Mobile, export CSV, registro transações, histórico patrimonial, celulose input, error handling, README | 7 |
| 5 — Chat Assessor | 2026/02/20 | OpenRouter LLM (llm.py, chat_prompts.py), Chat Assessor (substitui Thesis Board), KB refatorada (cards, filtros), seed teses, vision/streaming | 14 |
| 6 — Market Monitor | 2026/02/21 | yield_curve.py (pyettj + Treasury XML), global_markets.py, Markets page (índices, commodities, curva juros), sparklines, freshness badges, filtros preset, botão "Analisar" | 14 |
| 7 — QA Automation | 2026/02/21 | 311 testes (formatting, currency, seed, chat_prompts, portfolio, market_data, macro_data, yield_curve, global_markets, llm, db) + conftest fixtures | 13 |
| 8 — Bug Fixes | 2026/02/21 | Caixa/fundos no patrimônio, top movers semanais, model_key fix, exposição duplicada, freshness badge, colunas Positions, import CSV, seed 15 catalisadores | 12 |
| 9 — Ajustes Finais | 2026/02/21 | EWY em mapeamentos, catalisadores atualizados, ibov_10pct normalizado, CSV importer robusto | 4 |
| 10 — Security Fix | 2026/02/22 | Fix auth bypass (session_state + auth guards em 7 páginas), PR #11 | 1 |

**Total: 108 tasks concluídas, 321 testes passando em ~1.7s**

---

## Pendente — Ações Manuais

- [ ] Teste manual: chat (streaming, vision), salvar análise, atualizar posição, KB filtros
- [ ] ~~Tema dark/light~~ DEPRIORITIZADO (Streamlit não suporta toggle runtime)

---

## Notas

- Spec (modelo de dados, APIs): `docs/specs/PRD.md`
- Framework de análise: `knowledge_base/frameworks/framework_analise.md`
- Deep dives (18 arquivos): `knowledge_base/deepdives/`
- Chat usa OpenRouter (9 modelos). Antigo `4_thesis_board.py` → `4_chat.py`
