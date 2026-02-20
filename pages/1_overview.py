"""Página Overview — Visão de helicóptero do portfólio."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics.portfolio import (
    build_portfolio_df,
    calc_factor_exposure,
    calc_sector_allocation,
    calc_top_movers,
    calc_total_patrimony,
    calc_total_pnl,
)
from data.db import get_positions, get_theses, get_upcoming_catalysts
from data.market_data import fetch_all_quotes
from utils.formatting import fmt_brl, fmt_date, fmt_pct

st.header("📊 Overview")

# --- Carregar dados ---
positions = get_positions(active_only=True)
quotes = fetch_all_quotes()
df = build_portfolio_df(positions, quotes)

# ============================================================
# KPI Cards
# ============================================================

total = calc_total_patrimony(df)
pnl_abs, pnl_pct = calc_total_pnl(df)
cash_row = df[df["sector"] == "caixa"]
cash_value = cash_row["current_value_brl"].sum() if not cash_row.empty else 0
cash_pct = (cash_value / total * 100) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Patrimônio", fmt_brl(total, compact=True))
col2.metric("P&L Total", fmt_brl(pnl_abs, compact=True), fmt_pct(pnl_pct, sign=True))
col3.metric("Caixa", fmt_brl(cash_value, compact=True), fmt_pct(cash_pct))
col4.metric("Posições Ativas", f"{len(df[df['sector'] != 'caixa'])}")

# --- Semáforo de teses ---
theses = get_theses()
if theses:
    green = sum(1 for t in theses if t.get("status") == "GREEN")
    yellow = sum(1 for t in theses if t.get("status") == "YELLOW")
    red = sum(1 for t in theses if t.get("status") == "RED")
    st.markdown(f"**Teses:** 🟢 {green} | 🟡 {yellow} | 🔴 {red}")

st.markdown("---")

# ============================================================
# Alocação Setorial + Top Movers
# ============================================================

col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Alocação Setorial")
    sector_df = calc_sector_allocation(df)
    if not sector_df.empty:
        fig = px.pie(
            sector_df,
            values="value_brl",
            names="label",
            color="label",
            color_discrete_map={row["label"]: row["color"] for _, row in sector_df.iterrows()},
            hole=0.45,
        )
        fig.update_traces(textposition="outside", textinfo="label+percent")
        fig.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Top Movers (dia)")
    gainers, losers = calc_top_movers(df, n=3)

    if not gainers.empty:
        for _, row in gainers.iterrows():
            st.markdown(f"🟢 **{row['ticker']}** {fmt_pct(row['change_pct'], sign=True)}")
    if not losers.empty:
        for _, row in losers.iterrows():
            st.markdown(f"🔴 **{row['ticker']}** {fmt_pct(row['change_pct'], sign=True)}")
    if gainers.empty and losers.empty:
        st.info("Sem dados de variação disponíveis.")

st.markdown("---")

# ============================================================
# Exposição por Fator de Risco + Catalisadores
# ============================================================

col_left2, col_right2 = st.columns([3, 2])

with col_left2:
    st.subheader("Exposição por Fator de Risco")
    exposures = calc_factor_exposure(df)
    if exposures:
        factor_labels = {
            "selic_1pp": "Selic / Juros BR",
            "usdbrl_10pct": "USD/BRL (Câmbio)",
            "ibov_10pct": "Beta IBOV",
            "brent_10pct": "Brent (Petróleo)",
        }
        labels = [factor_labels.get(k, k) for k in exposures]
        values = list(exposures.values())

        fig_bar = go.Figure(
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color="#1f77b4",
                text=[f"{v:.1f}%" for v in values],
                textposition="auto",
            )
        )
        fig_bar.update_layout(
            xaxis_title="% do Portfólio Exposto",
            margin=dict(t=10, b=30, l=10, r=10),
            height=250,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with col_right2:
    st.subheader("Próximos Catalisadores")
    catalysts = get_upcoming_catalysts(limit=5)
    if catalysts:
        for cat in catalysts:
            impact_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(cat.get("impact", ""), "⚪")
            date_str = fmt_date(cat.get("expected_date"), short=True)
            st.markdown(f"{impact_icon} **{date_str}** — {cat['ticker']}: {cat['description']}")
    else:
        st.info("Nenhum catalisador cadastrado.")
