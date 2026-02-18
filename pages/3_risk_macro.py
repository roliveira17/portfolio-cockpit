"""Página Risk & Macro — Indicadores macro e métricas de risco."""

import numpy as np
import plotly.express as px
import streamlit as st
import yfinance as yf

from analytics.portfolio import build_portfolio_df
from data.db import get_positions
from data.macro_data import fetch_macro_br, fetch_macro_global
from data.market_data import fetch_all_quotes
from utils.constants import CACHE_TTL_QUOTES, TICKERS_BR, TICKERS_US
from utils.formatting import fmt_number, fmt_pct

# ============================================================
# Helpers
# ============================================================


def _safe_value(data: dict | None) -> float | None:
    if data is None:
        return None
    return data.get("value")


def _safe_change(data: dict | None) -> float | None:
    if data is None:
        return None
    return data.get("change_pct")


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def _calc_correlation_matrix():
    """Calcula matriz de correlação de retornos diários (90 dias)."""
    tickers_br_yf = [f"{t}.SA" for t in TICKERS_BR]
    all_tickers = tickers_br_yf + list(TICKERS_US)

    try:
        data = yf.download(all_tickers, period="3mo", progress=False)
        if data.empty:
            return None
        close = data["Close"]
        rename_map = {f"{t}.SA": t for t in TICKERS_BR}
        close = close.rename(columns=rename_map)
        returns = close.pct_change().dropna()
        if len(returns) < 10:
            return None
        return returns.corr()
    except Exception:
        return None


# ============================================================
# Layout
# ============================================================

st.header("⚠️ Risk & Macro")

tab_macro, tab_risk = st.tabs(["🌐 Macro Dashboard", "📉 Risk Dashboard"])

# ============================================================
# Tab 1: Macro Dashboard
# ============================================================

with tab_macro:
    macro_br = fetch_macro_br()
    macro_gl = fetch_macro_global()

    # KPI Cards — linha 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Selic", fmt_pct(macro_br.get("selic"), decimals=2))
    c2.metric(
        "USD/BRL",
        fmt_number(macro_br.get("usd_brl"), decimals=4),
    )

    ibov = macro_gl.get("ibov")
    c3.metric("IBOV", fmt_number(_safe_value(ibov), decimals=0), fmt_pct(_safe_change(ibov), sign=True))

    vix = macro_gl.get("vix")
    c4.metric("VIX", fmt_number(_safe_value(vix), decimals=1), fmt_pct(_safe_change(vix), sign=True))

    # KPI Cards — linha 2
    c5, c6, c7, c8 = st.columns(4)
    brent = macro_gl.get("brent")
    c5.metric(
        "Brent",
        f"US${_safe_value(brent):.1f}" if _safe_value(brent) else "—",
        fmt_pct(_safe_change(brent), sign=True),
    )

    dxy = macro_gl.get("dxy")
    c6.metric("DXY", fmt_number(_safe_value(dxy), decimals=1), fmt_pct(_safe_change(dxy), sign=True))

    sp500 = macro_gl.get("sp500")
    c7.metric("S&P 500", fmt_number(_safe_value(sp500), decimals=0), fmt_pct(_safe_change(sp500), sign=True))

    c8.metric("IPCA 12m", fmt_pct(macro_br.get("ipca_12m"), decimals=2))

    st.markdown("---")

    st.subheader("Matriz Macro → Impacto Estimado no Portfólio")
    st.markdown(
        """
| Cenário | Impacto Estimado |
|---------|-----------------|
| Selic +1pp | Portfólio ~-3% (posições sensíveis a juros) |
| BRL depreciar 10% | Portfólio ~-1% (exportadoras ganham, US perde convertido) |
| Brent -20% | BRAV3 ~-24% (alta sensibilidade) |
| IBOV -10% | Portfólio ~-8% (beta médio ~0.85) |
"""
    )

# ============================================================
# Tab 2: Risk Dashboard
# ============================================================

with tab_risk:
    positions = get_positions(active_only=True)
    quotes = fetch_all_quotes()
    df = build_portfolio_df(positions, quotes)

    # --- Correlation Matrix ---
    st.subheader("Correlation Matrix (90 dias)")
    corr_matrix = _calc_correlation_matrix()
    if corr_matrix is not None and not corr_matrix.empty:
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )
        fig_corr.update_layout(margin=dict(t=30, b=30), height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Dados insuficientes para calcular correlação.")

    st.markdown("---")

    # --- Concentração e Diversificação ---
    col_conc, col_div = st.columns(2)

    with col_conc:
        st.subheader("Concentração")
        weights = df[df["current_value_brl"] > 0]["weight"].values / 100
        if len(weights) > 0:
            hhi = float(np.sum(weights**2))
            effective_n = 1 / hhi if hhi > 0 else 0
            level = "Baixo" if hhi < 0.10 else "Moderado" if hhi < 0.18 else "Alto"
            st.metric("HHI", f"{hhi:.4f} ({level})")
            st.metric("Nº Efetivo de Posições", f"{effective_n:.1f}")

    with col_div:
        st.subheader("Diversificação")
        sorted_weights = sorted(df["weight"].values, reverse=True)
        if sorted_weights:
            st.markdown(f"**Top 1:** {sorted_weights[0]:.1f}%")
            st.markdown(f"**Top 3:** {sum(sorted_weights[:3]):.1f}%")
            st.markdown(f"**Top 5:** {sum(sorted_weights[:5]):.1f}%")
            n_sectors = df["sector"].nunique()
            n_currencies = df["currency"].nunique()
            st.markdown(f"**Setores:** {n_sectors} | **Moedas:** {n_currencies}")

    st.markdown("---")

    st.subheader("Risk Metrics")
    st.info(
        "Métricas avançadas (Sharpe, Sortino, Max Drawdown, VaR) "
        "serão calculadas na Sprint 3 com dados históricos do portfólio."
    )
