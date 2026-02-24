"""Página Overview — Visão de helicóptero do portfólio."""

from datetime import date

import pandas as pd
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
from data.db import (
    get_latest_portfolio_snapshot,
    get_portfolio_snapshots,
    get_positions,
    get_theses,
    get_upcoming_catalysts,
    save_portfolio_snapshot,
)
from data.market_data import fetch_all_quotes, fetch_weekly_changes
from utils.auth import check_auth
from utils.cache_info import record_fetch_time, show_freshness_badge
from utils.formatting import fmt_brl, fmt_date, fmt_pct

check_auth()

st.header("📊 Overview")

# --- Carregar dados ---
positions = get_positions(active_only=True)
if not positions:
    st.warning("Não foi possível carregar posições. Verifique a conexão com o Supabase.")
    st.stop()
quotes = fetch_all_quotes()
record_fetch_time("quotes")
df = build_portfolio_df(positions, quotes)

# ============================================================
# KPI Cards
# ============================================================

total = calc_total_patrimony(df)
pnl_abs, pnl_pct = calc_total_pnl(df)
cash_row = df[df["sector"] == "caixa"]
cash_value = cash_row["current_value_brl"].sum() if not cash_row.empty else 0
cash_pct = (cash_value / total * 100) if total > 0 else 0

show_freshness_badge("quotes", "Cotações")

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
# Patrimônio Histórico (Task 4.4)
# ============================================================

snapshots = get_portfolio_snapshots()
if snapshots and len(snapshots) >= 2:
    st.subheader("Evolução Patrimonial")
    snap_df = pd.DataFrame(snapshots)
    snap_df["date"] = pd.to_datetime(snap_df["date"])
    fig_hist = px.line(
        snap_df,
        x="date",
        y="total_value_brl",
        labels={"date": "", "total_value_brl": "Patrimônio (R$)"},
    )
    fig_hist.update_layout(
        height=250,
        margin=dict(t=20, b=30, l=10, r=10),
        yaxis_title="",
    )
    fig_hist.update_traces(line_color="#1f77b4")
    st.plotly_chart(fig_hist, use_container_width=True)
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
            color_discrete_map=dict(zip(sector_df["label"], sector_df["color"])),
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
    weekly = fetch_weekly_changes()
    if weekly:
        df["weekly_change_pct"] = df["ticker"].map(weekly)
        st.subheader("Top Movers (semana)")
        gainers, losers = calc_top_movers(df, n=5, change_col="weekly_change_pct")
        _change_col = "weekly_change_pct"
    else:
        st.subheader("Top Movers (dia)")
        gainers, losers = calc_top_movers(df, n=5)
        _change_col = "change_pct"

    if not gainers.empty:
        for _, row in gainers.iterrows():
            st.markdown(f"🟢 **{row['ticker']}** {fmt_pct(row[_change_col], sign=True)}")
    if not losers.empty:
        for _, row in losers.iterrows():
            st.markdown(f"🔴 **{row['ticker']}** {fmt_pct(row[_change_col], sign=True)}")
    if gainers.empty and losers.empty:
        st.info("Sem dados de variação disponíveis.")

st.markdown("---")

# ============================================================
# Exposição por Fator de Risco + Catalisadores
# ============================================================

col_left2, col_right2 = st.columns([3, 2])

with col_left2:
    st.subheader("Exposição por Fator de Risco")
    all_exposures = calc_factor_exposure(df)
    factor_labels = {
        "selic_1pp": "Selic / Juros BR",
        "usdbrl_10pct": "USD/BRL (Câmbio)",
        "brent_10pct": "Brent (Petróleo)",
    }
    exposures = {k: v for k, v in all_exposures.items() if k in factor_labels}
    if exposures:
        labels = [factor_labels[k] for k in exposures]
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

# ============================================================
# Auto-save snapshot diário (Task 3.8)
# ============================================================

_latest_snap = get_latest_portfolio_snapshot()
_today = str(date.today())
if not _latest_snap or _latest_snap.get("date") != _today:
    try:
        from utils.currency import brl_to_usd

        _valid = df[df["current_value_brl"].notna() & (df["current_value_brl"] > 0)]
        _positions_data = (
            _valid[["ticker", "current_value_brl"]]
            .rename(columns={"current_value_brl": "value_brl"})
            .to_dict("records")
        )
        save_portfolio_snapshot(
            {
                "date": _today,
                "total_value_brl": round(total, 2),
                "total_value_usd": round(brl_to_usd(total) or 0, 2),
                "cash_brl": round(cash_value, 2),
                "positions_data": _positions_data,
            }
        )
    except Exception:
        import logging

        logging.getLogger(__name__).warning("Falha ao salvar snapshot diario", exc_info=True)
