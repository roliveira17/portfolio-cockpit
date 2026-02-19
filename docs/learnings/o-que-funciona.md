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
