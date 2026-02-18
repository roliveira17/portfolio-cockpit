"""Página Positions — Visão detalhada de cada posição."""

import streamlit as st

from analytics.portfolio import build_portfolio_df
from data.db import get_positions
from data.market_data import fetch_all_quotes
from utils.formatting import fmt_brl, fmt_pct, fmt_usd

st.header("💼 Positions")

# --- Carregar dados ---
positions = get_positions(active_only=True)
quotes = fetch_all_quotes()
df = build_portfolio_df(positions, quotes)

# ============================================================
# Filtros
# ============================================================

col_f1, col_f2 = st.columns(2)
with col_f1:
    sectors = ["Todos"] + sorted(df["sector"].unique().tolist())
    selected_sector = st.selectbox("Filtro Setor", sectors)
with col_f2:
    markets = ["Todos", "BR", "US"]
    selected_market = st.selectbox("Filtro Mercado", markets)

filtered = df.copy()
if selected_sector != "Todos":
    filtered = filtered[filtered["sector"] == selected_sector]
if selected_market != "Todos":
    filtered = filtered[filtered["market"] == selected_market]

# ============================================================
# Tabela Principal
# ============================================================

st.subheader(f"Posições ({len(filtered)})")

display_cols = {
    "ticker": "Ticker",
    "company_name": "Empresa",
    "sector": "Setor",
    "weight": "Peso %",
    "target_weight": "Target %",
    "weight_gap": "Gap %",
    "current_price": "Preço Atual",
    "avg_price": "PM",
    "pnl_pct": "P&L %",
    "pnl_with_div_pct": "P&L c/ Div %",
    "change_pct": "Var. Dia %",
}

display_df = filtered[list(display_cols.keys())].rename(columns=display_cols)

st.dataframe(
    display_df.style.format(
        {
            "Peso %": "{:.1f}",
            "Target %": "{:.1f}",
            "Gap %": "{:+.1f}",
            "Preço Atual": "{:.2f}",
            "PM": "{:.2f}",
            "P&L %": "{:+.1f}",
            "P&L c/ Div %": "{:+.1f}",
            "Var. Dia %": "{:+.2f}",
        },
        na_rep="—",
    ).applymap(
        lambda v: (
            "color: #2ca02c"
            if isinstance(v, (int, float)) and v > 0
            else "color: #d62728"
            if isinstance(v, (int, float)) and v < 0
            else ""
        ),
        subset=["P&L %", "P&L c/ Div %", "Var. Dia %", "Gap %"],
    ),
    use_container_width=True,
    hide_index=True,
    height=min(35 * len(display_df) + 38, 600),
)

# ============================================================
# Detalhes da posição selecionada
# ============================================================

st.markdown("---")
st.subheader("Detalhes da Posição")

tickers = filtered["ticker"].tolist()
if tickers:
    selected_ticker = st.selectbox("Selecionar posição", tickers)
    row = filtered[filtered["ticker"] == selected_ticker].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{row['ticker']}** — {row['company_name']}")
        st.markdown(f"Setor: {row['sector']} | Mercado: {row['market']}")
        st.markdown(f"Quantidade: {row['quantity']:,.2f}")
        fmt_fn = fmt_brl if row["currency"] == "BRL" else fmt_usd
        st.markdown(f"Preço Médio: {fmt_fn(row['avg_price'])}")
        st.markdown(f"Preço Atual: {fmt_fn(row['current_price'])}")

    with col2:
        st.markdown("**P&L**")
        st.markdown(f"Investido: {fmt_fn(row['total_invested'])}")
        if row["current_value_original"]:
            st.markdown(f"Valor Atual: {fmt_fn(row['current_value_original'])}")
        st.markdown(f"P&L: {fmt_pct(row['pnl_pct'], sign=True)}")
        if row["dividends_received"] > 0:
            st.markdown(f"Dividendos: {fmt_fn(row['dividends_received'])}")
            st.markdown(f"P&L c/ Div: {fmt_pct(row['pnl_with_div_pct'], sign=True)}")

    with col3:
        st.markdown("**Alocação**")
        st.markdown(f"Peso Atual: {row['weight']:.1f}%")
        st.markdown(f"Peso Target: {row['target_weight']:.1f}%")
        gap = row["weight_gap"]
        gap_label = "overweight" if gap > 0 else "underweight" if gap < 0 else "on target"
        st.markdown(f"Gap: {gap:+.1f}% ({gap_label})")

# ============================================================
# Export CSV
# ============================================================

st.markdown("---")
csv = filtered.to_csv(index=False)
st.download_button("📥 Exportar CSV", csv, "positions.csv", "text/csv")
