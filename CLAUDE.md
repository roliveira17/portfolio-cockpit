# Portfolio Cockpit

Dashboard de monitoramento de portfólio de investimentos (family office, ~R$514k, ~20 posições BR+US).
Filosofia GARP (Growth at Reasonable Price). Uso semanal, desktop-first.

## Stack

- **Frontend/UI:** Streamlit (Python 3.12)
- **Gráficos:** Plotly
- **DB:** Supabase (PostgreSQL, free tier)
- **Dados de mercado:** brapi.dev (BR) + yfinance (US)
- **Dados macro:** BCB API + yfinance (FRED)
- **Analytics:** Pandas, NumPy, PyPortfolioOpt, quantstats
- **Deploy:** Streamlit Cloud
- **Gerenciamento:** uv (package manager)

## Comandos

```bash
uv sync                              # Instalar dependências
uv run streamlit run app.py          # Rodar local
uv run ruff check .                  # Lint
uv run ruff format .                 # Formatar
uv run pytest tests/ -x             # Testes (só analytics)
```

## Estrutura do Projeto

```
portfolio-cockpit/
├── app.py                          # Entry point Streamlit multipage
├── pages/                          # 7 páginas (overview, positions, risk_macro, chat, knowledge_base, simulator, markets)
├── data/                           # DB, APIs, LLM, seed (db, market_data, macro_data, llm, chat_prompts, yield_curve, global_markets, seed)
├── analytics/                      # Cálculos (portfolio, risk, performance, simulator)
├── utils/                          # Helpers (formatting, constants, currency, cache_info)
├── tests/                          # 321 testes (utils/, data/, analytics/)
├── knowledge_base/                 # Deep dives .md (seed no DB)
└── docs/                           # Specs, learnings, decisions
```

Referência compacta do modelo de dados e APIs: @docs/specs/PRD.md

## Workflow

1. **Leia a spec antes de implementar.** A spec é `docs/specs/PRD.md` (modelo de dados, APIs, requisitos).
2. **Leia o ROADMAP.md** para saber o estado atual.
3. **Se a spec não cobre algo**, pergunte. Não invente requisitos.
4. **Se descobrir que a spec precisa mudar**, proponha a mudança antes de implementar.

## Regras Críticas

**IMPORTANTE — Anti-Over-Engineering:**
- Se a solução simples funciona, use ela. Não abstraia prematuramente.
- Máximo 1 nível de abstração. Sem factory patterns, sem dependency injection, sem classes onde funções bastam.
- Funções fazem UMA coisa. Máximo ~50 linhas. Se passou, quebre.
- Arquivos máximo ~300 linhas. Se passou, sugira split.
- Sem código "pra futuro". Implemente o que a spec pede, nada mais.
- Prefira composição sobre herança. Prefira funções sobre classes.

**Código:**
- Código em inglês (variáveis, funções, docstrings).
- Commits em português, formato Conventional Commits: `tipo(escopo): descrição`
- Docs em português.
- Imports: stdlib → third-party → local, separados por linha em branco.
- Use f-strings. Use type hints em parâmetros de funções públicas.
- Nomes descritivos. Sem abreviações crípticas (`calc_portfolio_weights`, não `cpw`).

**Streamlit:**
- Use `st.cache_data` com TTL para dados de API (cotações: 15min, macro: 1h).
- Use `st.cache_resource` para conexão Supabase.
- Cada página é um arquivo em `pages/`. Lógica pesada fica em `data/` ou `analytics/`.
- Não coloque lógica de negócio nas páginas. Páginas = UI + chamadas a módulos.

**Dados:**
- Supabase para persistência. Variáveis de conexão em `.streamlit/secrets.toml`.
- NUNCA commitar secrets, .env, tokens.
- brapi.dev para cotações BR (fallback: yfinance com `.SA`).
- yfinance para cotações US e indicadores globais.
- Cache agressivo. Minimize chamadas de API.

**Testes:**
- 321 testes cobrindo `utils/`, `data/`, `analytics/` (tudo mockado, sem I/O real).
- Framework: pytest. Rodar: `uv run pytest tests/ -x`
- Não testar UI do Streamlit (alto custo, baixo retorno).
- Dados de teste: fixtures em `conftest.py` com valores conhecidos.

## Quando Algo Dá Errado

- Se uma API falhar (brapi, yfinance, BCB): mostrar último dado cacheado + aviso ao usuário. Nunca crashar.
- Se um cálculo der divisão por zero ou NaN: retornar None e mostrar "—" na UI.
- Se Supabase estiver fora: modo degradado com dados locais/cacheados.

## Convenções de Git

Para regras completas de Git, branches e PRs: @.claude/commands/git.md