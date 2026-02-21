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
