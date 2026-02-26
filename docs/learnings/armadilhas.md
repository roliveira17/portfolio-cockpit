# Armadilhas — Problemas Encontrados e Soluções

> Atualizado conforme encontramos problemas e soluções.

---

## 2026-02-18 — Smart App Control bloqueia Python/uv no Windows 11

**Problema:** O Windows 11 com Smart App Control ativado bloqueia a execução de Python em venvs criados pelo `uv`. Erro: `Uma política de Controle de Aplicativo bloqueou este arquivo (os error 4551)`. Afeta tanto o `uv sync` (build de pacotes como `multitasking`) quanto a criação de venvs.

**Solução:** Desativar o Smart App Control em:
Configurações → Privacidade e Segurança → Segurança do Windows → Controle de Aplicativo e Navegador → Smart App Control → Desativado.

**Nota:** Essa ação é irreversível sem reinstalar o Windows. Necessário reiniciar o PC após desativar.

---

## 2026-02-19 — Streamlit Cloud não lê pyproject.toml do uv

**Problema:** Streamlit Cloud não reconhece `pyproject.toml` com formato do `uv` para instalar dependências. O deploy falha silenciosamente sem instalar nada.

**Solução:** Criar `requirements.txt` na raiz com as dependências diretas (sem lock de versões transitivas). Manter `pyproject.toml` para uso local com `uv`.

---

## 2026-02-19 — Repo privado não aparece no Streamlit Cloud

**Problema:** Ao tentar deploy no Streamlit Cloud, repo privado do GitHub não aparece na lista. Mensagem "This repository does not exist".

**Causa:** O Streamlit OAuth App no GitHub só tinha permissão "Access public repositories".

**Solução:** Tornar o repo público, ou revogar/re-autorizar o Streamlit App com permissão para repos privados.

---

## 2026-02-20 — Encoding mojibake em deep dives do Supabase

**Problema:** Textos inseridos no Supabase com encoding duplo (UTF-8 → Latin-1 → UTF-8) resultam em mojibake: `Ã£` em vez de `ã`, `Ã§` em vez de `ç`.

**Causa:** O arquivo .md é UTF-8, mas ao ler/inserir pode ocorrer re-encoding dependendo do locale do sistema (Windows cp1252).

**Solução:** Helper `_fix_encoding(text)` que tenta `text.encode('latin-1').decode('utf-8')`. Se falhar (já estava correto), retorna o original. Aplicar tanto no seed quanto na renderização da KB.

---

## 2026-02-20 — requirements.txt precisa de TODAS as dependências para Streamlit Cloud

**Problema:** Ao adicionar `openai` como dependência no `pyproject.toml`, o deploy no Streamlit Cloud não a instala porque Streamlit Cloud lê `requirements.txt`, não `pyproject.toml`.

**Solução:** Sempre que adicionar dependência ao `pyproject.toml`, lembrar de adicionar também ao `requirements.txt`. São dois pontos de verdade — um para dev local (uv), outro para deploy (Streamlit Cloud).

---

## 2026-02-20 — Windows cp1252 ao parsear Python com ast.parse

**Problema:** `ast.parse(open('file.py').read())` falha no Windows com `UnicodeDecodeError` porque `open()` usa cp1252 por default, mas o arquivo tem UTF-8 com caracteres acentuados.

**Solução:** Sempre especificar encoding: `open('file.py', encoding='utf-8').read()`.

---

## 2026-02-21 — Strings acentuadas em assertions de teste no Windows

**Problema:** Assertions como `assert "posição" in result` falham no Windows porque o pytest lê o arquivo .py como cp1252 em vez de UTF-8, corrompendo os caracteres acentuados.

**Solução:** Evitar strings com acentos em assertions de testes. Usar alternativas sem acentos (ex: `"Atualizar carteira"` em vez de `"Atualizar posição da carteira"`).

---

## 2026-02-21 — `build_portfolio_df([], {})` levanta KeyError

**Problema:** Chamar `build_portfolio_df` com lista vazia de posições cria um DataFrame sem colunas, e o acesso subsequente a `df["current_value_brl"]` levanta `KeyError`.

**Solução:** Documentar no teste com `pytest.raises(KeyError)`. Comportamento aceitável — a UI checa se positions é vazio antes de chamar a função.

---

## 2026-02-21 — Posições de caixa/fundos sem cotação zeram patrimônio

**Problema:** Posições com `sector` "caixa" ou "fundos" não têm cotação de mercado (não existem na brapi/yfinance). `current_price` fica `None`, `current_value_brl` fica `None`, e ~R$143k de patrimônio (caixa + fundos) some do total.

**Solução:** Em `build_portfolio_df`, adicionar caminho especial: se `current_price is None` e `sector in ("caixa", "fundos")`, usar `total_invested` como valor atual e `P&L = 0`. O `continue` pula o cálculo normal de P&L.

---

## 2026-02-21 — Sensibilidades ibov_10pct em escala errada

**Problema:** `FACTOR_SENSITIVITIES["ibov_10pct"]` usava betas brutos (1.2, 0.6) enquanto os outros fatores usam impacto proporcional (-0.05, +0.08). Ao calcular stress test com IBOV -10%, INBR32 mostrava -120% em vez de -12%.

**Solução:** Dividir betas por 10 para converter para escala proporcional: beta 1.2 → 0.12 (= 12% de impacto quando IBOV move 10%). Adicionar comentário explicando a escala.

---

## 2026-02-25 — html5lib faltando faz curva DI nunca aparecer

**Problema:** A curva DI x Pré nunca aparecia na UI. A mensagem "Verifique se é dia útil" era mostrada mesmo em dias úteis. O `except Exception` em `yield_curve.py` engolia o `ImportError` real.

**Causa:** `pyettj` usa `pd.read_html(flavor="bs4")` internamente, que depende de `html5lib`. Sem essa lib, `pd.read_html` levanta `ImportError`, que era capturada pelo `except Exception` genérico.

**Solução:** Adicionar `html5lib>=1.1` às dependências. Melhorar o except para logar o erro específico em vez de mensagem genérica. Melhorar mensagem da UI para "Pode ser feriado ou problema de conexão" (mais honesto).

**Lição:** Dependências transitivas implícitas (lib A precisa de lib B que não está no requirements) são armadilhas silenciosas. `except Exception` sem logging do erro real é a pior combinação — esconde o problema completamente.
