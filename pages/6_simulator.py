"""Página Simulator — Simulação what-if do portfólio."""

import pandas as pd
import streamlit as st

from analytics.portfolio import build_portfolio_df
from analytics.risk import (
    calc_stress_test_portfolio,
    get_predefined_scenarios,
)
from analytics.simulator import simulate_new_trade, simulate_rebalance
from data.db import get_positions
from data.market_data import fetch_all_quotes
from utils.auth import check_auth
from utils.formatting import fmt_brl, fmt_pct

check_auth()

st.header("🔬 Simulator")

# --- Carregar dados ---
positions = get_positions(active_only=True)
if not positions:
    st.warning("Não foi possível carregar posições. Verifique a conexão com o Supabase.")
    st.stop()
quotes = fetch_all_quotes()
df = build_portfolio_df(positions, quotes)

# Posições de ações (excluir fundos e caixa)
stock_df = df[~df["sector"].isin(["fundos", "caixa"])].copy()
all_tickers = stock_df["ticker"].tolist()

mode = st.radio(
    "Tipo de Simulação",
    ["Rebalanceamento", "Stress Test", "New Trade"],
    horizontal=True,
)

st.markdown("---")

# ============================================================
# Modo 1: Rebalanceamento (3.3)
# ============================================================

if mode == "Rebalanceamento":
    st.subheader("Ajuste os pesos-alvo")

    new_weights = {}
    cols_per_row = 3

    for i in range(0, len(all_tickers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(all_tickers):
                break
            ticker = all_tickers[idx]
            row = stock_df[stock_df["ticker"] == ticker].iloc[0]
            current = float(row["weight"])
            target = float(row["target_weight"])
            with col:
                new_w = st.slider(
                    f"{ticker} ({current:.1f}%)",
                    min_value=0.0,
                    max_value=30.0,
                    value=target,
                    step=0.5,
                    key=f"rebal_{ticker}",
                )
                new_weights[ticker] = new_w

    # Manter pesos de fundos e caixa inalterados
    remaining = df[~df["ticker"].isin(new_weights.keys())]
    for ticker, weight in zip(remaining["ticker"], remaining["weight"]):
        new_weights[ticker] = float(weight)

    if st.button("📊 Simular Rebalanceamento"):
        result = simulate_rebalance(df, new_weights)

        st.markdown("### Trades Necessários")
        if result["trades"]:
            trades_df = pd.DataFrame(result["trades"])
            st.dataframe(trades_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum trade necessário (pesos já atingidos).")

        st.markdown("### Impacto")
        ic1, ic2 = st.columns(2)
        with ic1:
            st.metric("HHI", f"{result['hhi_new']:.4f}", f"{result['hhi_new'] - result['hhi_old']:+.4f}")
        with ic2:
            old_exp = result["exposure_old"]
            new_exp = result["exposure_new"]
            factor_labels = {
                "selic_1pp": "Selic",
                "usdbrl_10pct": "USD/BRL",
                "ibov_10pct": "IBOV",
                "brent_10pct": "Brent",
            }
            exp_rows = []
            for k in old_exp:
                exp_rows.append(
                    {
                        "Fator": factor_labels.get(k, k),
                        "Atual (%)": f"{old_exp[k]:.1f}",
                        "Novo (%)": f"{new_exp.get(k, 0):.1f}",
                    }
                )
            if exp_rows:
                st.dataframe(pd.DataFrame(exp_rows), use_container_width=True, hide_index=True)

# ============================================================
# Modo 2: Stress Test (3.4 + 3.6)
# ============================================================

elif mode == "Stress Test":
    st.subheader("Cenário de Stress")

    scenarios = get_predefined_scenarios()
    scenario_names = ["Personalizado"] + list(scenarios.keys())
    selected = st.selectbox("Cenário pré-definido", scenario_names)

    if selected != "Personalizado":
        defaults = scenarios[selected]
    else:
        defaults = {"selic_1pp": 0.0, "usdbrl_10pct": 0.0, "brent_10pct": 0.0, "ibov_10pct": 0.0}

    sc1, sc2 = st.columns(2)
    with sc1:
        selic_shock = st.slider(
            "Selic (pp)",
            min_value=-2.0,
            max_value=3.0,
            value=defaults.get("selic_1pp", 0.0),
            step=0.25,
        )
        brent_shock = st.slider(
            "Brent (%)",
            min_value=-30.0,
            max_value=30.0,
            value=defaults.get("brent_10pct", 0.0),
            step=5.0,
        )
    with sc2:
        usdbrl_shock = st.slider(
            "USD/BRL (%)",
            min_value=-15.0,
            max_value=20.0,
            value=defaults.get("usdbrl_10pct", 0.0),
            step=1.0,
        )
        ibov_shock = st.slider(
            "IBOV (%)",
            min_value=-25.0,
            max_value=25.0,
            value=defaults.get("ibov_10pct", 0.0),
            step=1.0,
        )

    shocks = {
        "selic_1pp": selic_shock,
        "usdbrl_10pct": usdbrl_shock,
        "brent_10pct": brent_shock,
        "ibov_10pct": ibov_shock,
    }

    if st.button("📊 Simular Stress Test"):
        result = calc_stress_test_portfolio(df, shocks)

        st.markdown("### Resultado")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric(
            "Impacto Total",
            fmt_pct(result["total_impact_pct"], sign=True),
        )
        rc2.metric("Impacto (R$)", fmt_brl(result["total_impact_brl"]))
        rc3.metric("Patrimônio Estimado", fmt_brl(result["new_total_brl"]))

        st.markdown("### Impacto por Posição")
        per_pos = [p for p in result["per_position"] if abs(p["impact_pct"]) > 0.01]
        if per_pos:
            pos_df = pd.DataFrame(per_pos)
            pos_df = pos_df.sort_values("impact_pct")
            display_cols = ["ticker", "current_value_brl", "impact_pct", "impact_brl", "new_value_brl"]
            renamed = pos_df[display_cols].rename(
                columns={
                    "ticker": "Ticker",
                    "current_value_brl": "Valor Atual (R$)",
                    "impact_pct": "Impacto (%)",
                    "impact_brl": "Impacto (R$)",
                    "new_value_brl": "Novo Valor (R$)",
                }
            )
            st.dataframe(renamed, use_container_width=True, hide_index=True)
            csv_stress = renamed.to_csv(index=False)
            st.download_button(
                "📥 Exportar CSV",
                csv_stress,
                "stress_test.csv",
                "text/csv",
            )

# ============================================================
# Modo 3: New Trade (3.5)
# ============================================================

elif mode == "New Trade":
    st.subheader("Simular Operação")

    tc1, tc2 = st.columns(2)
    with tc1:
        action = st.selectbox("Ação", ["COMPRAR", "VENDER"])
        trade_ticker = st.selectbox("Ticker", all_tickers)
    with tc2:
        row_sel = stock_df[stock_df["ticker"] == trade_ticker]
        has_price = not row_sel.empty and row_sel.iloc[0]["current_price"]
        default_price = float(row_sel.iloc[0]["current_price"]) if has_price else 0.0
        trade_qty = st.number_input("Quantidade", min_value=1, value=100, step=1)
        trade_price = st.number_input("Preço", min_value=0.01, value=default_price, step=0.01)

    if st.button("📊 Simular Trade"):
        result = simulate_new_trade(df, trade_ticker, action, trade_qty, trade_price)

        if result:
            st.markdown("### Resultado")
            nr1, nr2 = st.columns(2)
            with nr1:
                st.metric(
                    f"Peso {trade_ticker}",
                    f"{result['new_weight']:.1f}%",
                    f"{result['new_weight'] - result['old_weight']:+.1f}pp",
                )
                st.metric(
                    "HHI",
                    f"{result['hhi_new']:.4f}",
                    f"{result['hhi_new'] - result['hhi_old']:+.4f}",
                )
            with nr2:
                st.metric(
                    "Caixa",
                    fmt_brl(result["new_cash"]),
                    fmt_brl(result["cash_impact_brl"]),
                )
        else:
            st.error("Não foi possível simular o trade.")
