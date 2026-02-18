# Armadilhas — Problemas Encontrados e Soluções

> Atualizado conforme encontramos problemas e soluções.

---

## 2026-02-18 — Smart App Control bloqueia Python/uv no Windows 11

**Problema:** O Windows 11 com Smart App Control ativado bloqueia a execução de Python em venvs criados pelo `uv`. Erro: `Uma política de Controle de Aplicativo bloqueou este arquivo (os error 4551)`. Afeta tanto o `uv sync` (build de pacotes como `multitasking`) quanto a criação de venvs.

**Solução:** Desativar o Smart App Control em:
Configurações → Privacidade e Segurança → Segurança do Windows → Controle de Aplicativo e Navegador → Smart App Control → Desativado.

**Nota:** Essa ação é irreversível sem reinstalar o Windows. Necessário reiniciar o PC após desativar.
