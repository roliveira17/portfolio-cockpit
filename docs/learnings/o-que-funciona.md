# O Que Funciona — Padrões e Práticas

> Atualizado conforme descobrimos o que funciona bem no projeto.

---

## 2026-02-18 — Sessão 2: Sprint 1 completa (infra → UI)

**Supabase CLI para setup de banco:**
- `npx supabase projects create` + `supabase init` + `supabase link` + `supabase db push` funciona perfeitamente. Evita mexer no dashboard web.
- Migrations SQL versionadas em `supabase/migrations/` ficam no Git — boa rastreabilidade.

**Fallback em APIs de mercado:**
- brapi.dev requer token (sem token retorna vazio, não erro). Fallback para yfinance com `.SA` funciona bem para cotações BR.
- yfinance `fast_info` é mais rápido que `info` para dados básicos (preço, volume).

**Estrutura de módulos com funções simples:**
- `data/db.py` com helpers genéricos (`fetch_all`, `insert_row`, etc.) + funções específicas por tabela mantém o código enxuto (~178 linhas para 8 tabelas).
- Separar `utils/constants.py` cedo evita magic numbers espalhados.

**Streamlit `st.navigation` para multipage:**
- Usar `st.Page("pages/arquivo.py")` com `st.navigation()` é mais limpo que a antiga convenção de nomes com emojis nos arquivos.

**Cache agressivo com `st.cache_data(ttl=...)`:**
- TTLs definidos em `constants.py` (CACHE_TTL_QUOTES=15min, CACHE_TTL_MACRO=1h) simplificam manutenção.

---

## 2026-02-19 — Sessão 3: Deploy + Sprint 2 completa

**Streamlit Cloud deploy:**
- Streamlit Cloud **não suporta** `pyproject.toml` do uv. Precisa de `requirements.txt` com dependências diretas.
- Repos privados precisam autorização explícita do Streamlit GitHub App. Alternativa simples: tornar repo público.
- Secrets no dashboard do Streamlit Cloud: mesma estrutura do `secrets.toml` local.

**Seed de Knowledge Base com regex parsing:**
- Extrair título (H1), resumo (seção "RESUMO" ou "SUMÁRIO"), analista e data de .md via regex é robusto o suficiente.
- SUZB3 é caso especial — deep dive está em `reports/tese_suzb3_atualizada.md`, não em `deepdives/`. Tratar no seed explicitamente.
- Pattern de delete-before-insert para idempotência do seed funciona bem.

**Streamlit forms para CRUD:**
- `st.form()` + `st.form_submit_button()` previne re-runs a cada interação com widgets. Essencial para páginas com muitos inputs como Thesis Board.
- Kill switches como `text_area` (um por linha) → `list[str]` na serialização é simples e funcional.

**Arquitetura de constantes com dicts ricos:**
- `THESIS_STATUS = {"GREEN": {"emoji": "🟢", "label": "Ativa"}}` é melhor que strings simples — permite formatar em selectbox e cards sem lógica extra.

**Versionamento de deep dives:**
- `get_next_deep_dive_version(ticker)` com `max(version) + 1` é simples e confiável.
- UNIQUE constraint `(ticker, version)` no Supabase garante integridade.

---

## 2026-02-19 — Sessão 4: Sprints 3 e 4 completas

**Pandas/NumPy puro para métricas financeiras:**
- quantstats tem conflitos com Streamlit (matplotlib backend). Implementar Sharpe, Sortino, VaR, drawdown com pandas/numpy é simples (~120 linhas) e sem conflitos.

**Stress tests com FACTOR_SENSITIVITIES:**
- Dict de sensibilidades por fator/ticker em `constants.py` é suficiente para stress tests básicos.
- Cada fator tem uma escala (selic = por pp, câmbio/brent/ibov = por 10%). Dividir o shock pela escala antes de multiplicar pela sensibilidade.

**Snapshot por page load (anti-cron):**
- Salvar portfolio snapshot no primeiro acesso do dia (verificar data do último) é mais simples que scheduler.
- Pattern: `if not latest or latest.date != today: save()` com try/except silencioso.

**Error handling em camada de dados:**
- Wrapping todas as queries do db.py com try/except + retorno [] ou None evita crashes em cascata.
- Pages fazem `if not positions: st.warning(); st.stop()` — modo degradado com mensagem clara.

**Execução sequencial vs subagents para código interdependente:**
- Módulos com imports cruzados (risk←performance, simulator←risk) devem ser escritos sequencialmente.
- Subagents são úteis apenas para exploração/planejamento, não para geração de código acoplado.

---

## 2026-02-20 — Sessão 5: Sprint 5 (Chat Assessor + KB refactor)

**OpenRouter como gateway de LLMs:**
- Usar OpenRouter com o SDK `openai` (mesma interface) permite trocar modelos sem mudar código. Basta `base_url="https://openrouter.ai/api/v1"`.
- Dict `OPENROUTER_MODELS` em constants.py com `id`, `supports_vision` e custo estimado por sessão facilita UI de seleção.

**Subagents em paralelo para tasks independentes:**
- Tasks sem dependência entre si (seed theses, DB helpers, KB refactor) rodam bem em paralelo como background agents.
- Um único agent pode cobrir múltiplas tasks se o escopo é coeso (ex: KB refactor agent fez 5.9 + 5.10 + 5.11).

**Streaming com `st.write_stream()`:**
- O generator retornado por `stream_chat_response()` funciona direto com `st.write_stream()` — Streamlit renderiza chunk a chunk.
- Não precisa acumular texto manualmente; `st.write_stream()` retorna o texto completo ao final.

**Helpers definidos antes do uso em Streamlit pages:**
- Em arquivos Streamlit com `st.chat_input`, `st.button`, etc., funções helper devem ser definidas ANTES do código de UI que as referencia. Caso contrário, o Streamlit executa top-to-bottom e encontra `NameError`.

**Extração de dados estruturados via LLM (two-step):**
- Passo 1: detectar intent via regex (barato, sem API call)
- Passo 2: se intent detectado, chamar LLM com prompt de extração JSON
- Prompt de extração com schema JSON explícito + "retorne null se insuficiente" evita falsos positivos.

---

## 2026-02-21 — Sessão 6: Sprint 6 (Market Monitor & UX)

**pyettj para curva DI x Pré:**
- `import pyettj.ettj as ettj` → `ettj.get_ettj(date, curva="PRE")` retorna DataFrame com `dias corridos` e `taxa`.
- Data no formato DD/MM/YYYY. Só funciona em dias úteis. Wrappear com try/except.
- Nomes de colunas podem variar — normalizar via pattern matching (`"dia"` + `"corr"` → `dias_corridos`).

**Treasury XML feed (beautifulsoup4):**
- URL: `home.treasury.gov/.../xml?data=daily_treasury_yield_curve&field_tdr_date_value=YYYY`
- Parse com `BeautifulSoup(content, "xml")` — tags como `BC_10YEAR`, `d:NEW_DATE`.
- Último `<entry>` é o mais recente. Extrair `text[:10]` para data.

**`st.column_config.LineChartColumn` para sparklines:**
- Requer lista de floats por célula do DataFrame. Ex: `df["spark"] = df["ticker"].apply(lambda t: prices[t][-20:])`
- `color="auto"` → verde se subiu, vermelho se caiu (compara primeiro vs último valor).
- Incompatível com `.style.format()` — precisa usar `column_config` no lugar de Styler.

**Freshness badge simples e efetivo:**
- `session_state["_cache_timestamps"]` para rastrear quando dados foram atualizados.
- `st.caption()` com emoji colorido (🟢/🟡/🟠) por faixa de tempo. Mínimo esforço, máximo valor.

---

## 2026-02-21 — Sessão 7: Sprint 7 (QA Test Automation)

**Bypass de `@st.cache_data` em testes:**
- Funções decoradas com `@st.cache_data` expõem a função original via `func.__wrapped__()`. Chamar `__wrapped__()` nos testes evita dependência do Streamlit runtime e cache.

**Mock de pyettj com `patch.dict(sys.modules)`:**
- `import pyettj.ettj as ettj` dentro de funções pega o atributo `.ettj` do módulo pai (MagicMock cria atributos automaticamente). Solução: criar mock pai com `.ettj = mock_ettj` explicitamente, e patchar ambos em `sys.modules`.
- Pattern: `_make_pyettj_mock(return_df)` que retorna `(mock_pyettj, mock_ettj)` + `importlib.reload(data.yield_curve)` para forçar re-import.

**Chainable MagicMock para Supabase:**
- Pattern `_make_mock_client(data)` que configura `.table().select().eq().order().limit().execute().data` de uma vez. Cada método retorna o mesmo `table_mock`, e `.execute()` retorna um mock com `.data` configurável.

**Fixtures compartilhadas em conftest.py:**
- `sample_brapi_response`, `sample_treasury_xml`, `mock_supabase_client`, `sample_positions_data`, `sample_quotes` — 5 fixtures reutilizadas em múltiplos test files evitam duplicação massiva.

**Testes 100% mockados = rápidos e confiáveis:**
- 311 testes em ~1.6s sem nenhuma chamada real a APIs/DB. Bom para CI/CD. Zero flakiness.

---

## 2026-02-21 — Sessões 8-9: Bug Fixes Overview/Positions + CSV Importer

**Importador CSV com detecção de formato BR/EN:**
- Verificar se primeira linha contém `;` para detectar separador brasileiro. Fallback: `pd.read_csv(io.StringIO(content))`.
- Decimal brasileiro: `str.replace(".", "").replace(",", ".")` converte `1.234,56` → `1234.56`.
- Preview da importação antes de aplicar (tabela com ação ATUALIZAR/CRIAR) evita erros silenciosos.
- Criar novas posições para tickers desconhecidos com inferência de mercado/moeda via regex (`\d$` → BR/BRL).

**Diagnóstico top-down de bugs financeiros:**
- Quando múltiplos KPIs estão errados (P&L NaN, Caixa R$0, patrimônio ~R$370k), traçar o fluxo de dados até a função central (`build_portfolio_df`) revela causa raiz única.
- pandas `None` → `NaN` silenciosamente. `if value is None` NÃO captura `NaN` — usar `pd.isna(value)`.

**Escala de sensibilidades em stress tests:**
- Todos os fatores devem usar a MESMA escala (impacto proporcional por unidade). Betas de IBOV (1.2) devem ser divididos por 10 para ficarem na escala dos outros fatores (0.12 = 12% quando IBOV move 10%).
- Fórmula: `impact = sensitivity × (shock / scale)`. Se escala de ibov é 10%, beta 1.2 deveria ser 0.12 (não 1.2).

**Model selection para LLMs com fallback chain:**
- Ordem de preferência: Flash/mini (baratos, rápidos) → Haiku → qualquer outro. Usar `next((k for k in MODELS if "Flash" in k or "mini" in k), fallback)`.
- Validar model IDs contra a API real — IDs podem mudar entre versões.
