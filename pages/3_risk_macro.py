"""Página Risk & Macro — Indicadores macro e métricas de risco."""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

from analytics.performance import (
    calc_beta_vs_benchmark,
    calc_drawdown_series,
    calc_max_drawdown,
    calc_portfolio_returns,
    calc_sharpe_ratio,
    calc_sortino_ratio,
    calc_volatility,
)
from analytics.portfolio import build_portfolio_df
from analytics.risk import calc_stress_test_portfolio, calc_var_historical
from data.db import get_positions
from data.macro_data import fetch_macro_br, fetch_macro_global
from data.market_data import fetch_all_quotes, fetch_batch_price_history
from utils.cache_info import record_fetch_time, show_freshness_badge
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

show_freshness_badge("macro", "Dados Macro")

tab_macro, tab_risk = st.tabs(["🌐 Macro Dashboard", "📉 Risk Dashboard"])

# ============================================================
# Tab 1: Macro Dashboard
# ============================================================

with tab_macro:
    macro_br = fetch_macro_br()
    macro_gl = fetch_macro_global()
    record_fetch_time("macro")

    # KPI Cards — linha 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Selic", fmt_pct(macro_br.get("selic"), decimals=2))
    c2.metric("USD/BRL", fmt_number(macro_br.get("usd_brl"), decimals=4))

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

    # --- Celulose BHKP (input manual - Task 4.6) ---
    st.markdown("---")
    st.subheader("Celulose BHKP")
    bhkp_col1, bhkp_col2 = st.columns([2, 3])
    with bhkp_col1:
        bhkp_price = st.number_input(
            "Preço BHKP (USD/ton)",
            min_value=0.0,
            step=1.0,
            value=st.session_state.get("bhkp_price", 0.0),
            help="Inserir manualmente. Fonte: Fastmarkets ou relatórios setoriais.",
        )
        st.session_state["bhkp_price"] = bhkp_price
    with bhkp_col2:
        if bhkp_price > 0:
            st.metric("BHKP", f"US$ {bhkp_price:.0f}/ton")
        else:
            st.info("Insira o preço atual da celulose BHKP manualmente.")

    st.markdown("---")

    # --- Stress Matrix dinâmico ---
    st.subheader("Matriz Macro → Impacto Estimado no Portfólio")
    _positions = get_positions(active_only=True)
    _quotes = fetch_all_quotes()
    _df_stress = build_portfolio_df(_positions, _quotes)

    default_shocks = [
        ("Selic +1pp", {"selic_1pp": 1.0}),
        ("USD/BRL +10%", {"usdbrl_10pct": 10.0}),
        ("Brent -20%", {"brent_10pct": -20.0}),
        ("IBOV -10%", {"ibov_10pct": -10.0}),
    ]
    stress_rows = []
    for label, shocks in default_shocks:
        result = calc_stress_test_portfolio(_df_stress, shocks)
        stress_rows.append(
            {
                "Cenário": label,
                "Impacto (%)": f"{result['total_impact_pct']:+.1f}%",
                "Impacto (R$)": f"R$ {result['total_impact_brl']:+,.0f}",
            }
        )
    st.dataframe(pd.DataFrame(stress_rows), use_container_width=True, hide_index=True)

# ============================================================
# Tab 2: Risk Dashboard
# ============================================================

with tab_risk:
    positions = get_positions(active_only=True)
    quotes = fetch_all_quotes()
    df = build_portfolio_df(positions, quotes)

    # --- Correlation Matrix ---
    with st.expander("Correlation Matrix (90 dias)", expanded=True):
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

    # --- Risk Metrics ---
    st.subheader("Risk Metrics")

    # Buscar histórico e calcular retornos
    price_hist = fetch_batch_price_history(
        tickers_br=TICKERS_BR,
        tickers_us=TICKERS_US,
        period="6mo",
    )
    weight_map = {row["ticker"]: row["weight"] / 100 for _, row in df.iterrows() if row["weight"] > 0}
    port_returns = calc_portfolio_returns(price_hist, weight_map) if price_hist is not None else None

    if port_returns is not None and len(port_returns) >= 20:
        selic = macro_br.get("selic")
        rf = selic / 100 if selic else 0.1325

        # Benchmark returns (IBOV)
        ibov_hist = fetch_batch_price_history(tickers_us=["^BVSP"], period="6mo")
        ibov_returns = None
        if ibov_hist is not None and "^BVSP" in ibov_hist.columns:
            ibov_returns = ibov_hist["^BVSP"].pct_change().dropna()

        sharpe = calc_sharpe_ratio(port_returns, rf)
        sortino = calc_sortino_ratio(port_returns, rf)
        max_dd = calc_max_drawdown(port_returns)
        vol_30 = calc_volatility(port_returns, window=30)
        beta = calc_beta_vs_benchmark(port_returns, ibov_returns)
        var_95 = calc_var_historical(port_returns, confidence=0.95)

        rm1, rm2, rm3 = st.columns(3)
        rm1.metric("Sharpe (vs CDI)", f"{sharpe:.2f}" if sharpe is not None else "—")
        rm2.metric("Sortino", f"{sortino:.2f}" if sortino is not None else "—")
        rm3.metric("Max Drawdown", fmt_pct(max_dd * 100, sign=True) if max_dd is not None else "—")

        rm4, rm5, rm6 = st.columns(3)
        rm4.metric("Vol. 30d (anual.)", fmt_pct(vol_30 * 100) if vol_30 is not None else "—")
        rm5.metric("Beta vs IBOV", f"{beta:.2f}" if beta is not None else "—")
        rm6.metric("VaR 95% (1d)", fmt_pct(var_95 * 100, sign=True) if var_95 is not None else "—")

        # --- Drawdown Chart ---
        st.markdown("---")
        st.subheader("Drawdown")
        dd_series = calc_drawdown_series(port_returns)
        if dd_series is not None and not dd_series.empty:
            dd_df = pd.DataFrame({"Data": dd_series.index, "Drawdown (%)": dd_series.values * 100})
            fig_dd = px.area(dd_df, x="Data", y="Drawdown (%)")
            fig_dd.update_layout(
                height=250,
                margin=dict(t=20, b=30),
                yaxis_title="",
                xaxis_title="",
            )
            fig_dd.update_traces(fillcolor="rgba(255, 0, 0, 0.3)", line_color="red")
            st.plotly_chart(fig_dd, use_container_width=True)
    else:
        st.info("Dados históricos insuficientes para calcular métricas de risco.")
