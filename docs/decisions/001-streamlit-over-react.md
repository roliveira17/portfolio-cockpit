# ADR 001 — Streamlit sobre React

**Data:** 2026-02-18
**Status:** Aceita

## Contexto

Precisamos de um framework para o dashboard do portfólio. As opções eram React + API backend ou Streamlit full-stack Python.

## Decisão

Streamlit, por ser nativo em Python (ecossistema financeiro), rápido de desenvolver, e ter deploy gratuito no Streamlit Cloud.

## Consequências

- (+) Desenvolvimento rápido, sem frontend separado
- (+) Integração nativa com Pandas, Plotly, NumPy
- (+) Deploy zero-config no Streamlit Cloud
- (-) Menos flexibilidade de UI que React
- (-) Limitações de state management (mitigado com st.session_state)
