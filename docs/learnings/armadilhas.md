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
