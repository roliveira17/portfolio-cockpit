"""Engine de simulação: rebalanceamento, new trade, impacto em portfólio."""

import numpy as np
import pandas as pd

from analytics.portfolio import calc_factor_exposure
from utils.currency import usd_to_brl


def simulate_rebalance(
    portfolio_df: pd.DataFrame,
    new_target_weights: dict[str, float],
) -> dict:
    """Simula rebalanceamento para novos pesos-alvo.

    Args:
        portfolio_df: DataFrame do portfólio (build_portfolio_df).
        new_target_weights: {ticker: peso_alvo_%} para posições de ações.

    Returns:
        dict com trades, hhi_old, hhi_new, exposure_old, exposure_new.
    """
    total = portfolio_df["current_value_brl"].sum()
    if total <= 0:
        return {"trades": [], "hhi_old": 0, "hhi_new": 0, "exposure_old": {}, "exposure_new": {}}

    old_weights = portfolio_df["weight"].values
    hhi_old = _calc_hhi(old_weights.tolist())
    exposure_old = calc_factor_exposure(portfolio_df)

    trades = []
    new_weights_list = []

    for _, row in portfolio_df.iterrows():
        ticker = row["ticker"]
        current_weight = row["weight"]
        target_weight = new_target_weights.get(ticker, current_weight)
        new_weights_list.append(target_weight)

        diff_pct = target_weight - current_weight
        if abs(diff_pct) < 0.1:
            continue

        diff_value = (diff_pct / 100) * total
        price = row["current_price"]
        if not price or price <= 0:
            continue

        # Converter preço para BRL se necessário
        price_brl = usd_to_brl(price) if row["currency"] == "USD" else price
        if not price_brl or price_brl <= 0:
            continue

        qty = abs(diff_value) / price_brl
        trades.append(
            {
                "ticker": ticker,
                "action": "COMPRAR" if diff_pct > 0 else "VENDER",
                "quantity": round(qty, 0),
                "value_brl": round(abs(diff_value), 2),
            }
        )

    hhi_new = _calc_hhi(new_weights_list)

    # Recalcular exposure com novos pesos simulados
    sim_df = portfolio_df.copy()
    for i, row in sim_df.iterrows():
        ticker = row["ticker"]
        new_w = new_target_weights.get(ticker, row["weight"])
        sim_df.at[i, "current_value_brl"] = total * (new_w / 100)
    exposure_new = calc_factor_exposure(sim_df)

    return {
        "trades": trades,
        "hhi_old": round(hhi_old, 4),
        "hhi_new": round(hhi_new, 4),
        "exposure_old": exposure_old,
        "exposure_new": exposure_new,
    }


def simulate_new_trade(
    portfolio_df: pd.DataFrame,
    ticker: str,
    action: str,
    quantity: float,
    price: float,
) -> dict:
    """Simula impacto de uma nova operação no portfólio.

    Args:
        portfolio_df: DataFrame do portfólio.
        ticker: Ticker da ação.
        action: "COMPRAR" ou "VENDER".
        quantity: Quantidade de ações.
        price: Preço por ação (moeda original).

    Returns:
        dict com old/new weight, cash, hhi, exposure.
    """
    total = portfolio_df["current_value_brl"].sum()
    if total <= 0:
        return {}

    row = portfolio_df[portfolio_df["ticker"] == ticker]
    is_usd = False
    if not row.empty:
        old_weight = float(row.iloc[0]["weight"])
        is_usd = row.iloc[0]["currency"] == "USD"
    else:
        old_weight = 0.0

    trade_value = quantity * price
    trade_value_brl = usd_to_brl(trade_value) if is_usd else trade_value
    if not trade_value_brl:
        trade_value_brl = trade_value

    cash_row = portfolio_df[portfolio_df["sector"] == "caixa"]
    old_cash = float(cash_row["current_value_brl"].sum()) if not cash_row.empty else 0

    if action == "COMPRAR":
        new_total = total  # total não muda (caixa → ação)
        new_cash = old_cash - trade_value_brl
        old_value = float(row.iloc[0]["current_value_brl"]) if not row.empty else 0
        new_value = old_value + trade_value_brl
    else:
        new_total = total
        new_cash = old_cash + trade_value_brl
        old_value = float(row.iloc[0]["current_value_brl"]) if not row.empty else 0
        new_value = max(0, old_value - trade_value_brl)

    new_weight = (new_value / new_total * 100) if new_total > 0 else 0

    # HHI
    old_weights = portfolio_df["weight"].values.tolist()
    hhi_old = _calc_hhi(old_weights)

    new_weights = old_weights.copy()
    for i, r in portfolio_df.iterrows():
        if r["ticker"] == ticker:
            new_weights[i] = new_weight
        elif r["sector"] == "caixa":
            new_weights[i] = (new_cash / new_total * 100) if new_total > 0 else 0
    hhi_new = _calc_hhi(new_weights)

    return {
        "old_weight": round(old_weight, 2),
        "new_weight": round(new_weight, 2),
        "old_cash": round(old_cash, 2),
        "new_cash": round(new_cash, 2),
        "cash_impact_brl": round(new_cash - old_cash, 2),
        "hhi_old": round(hhi_old, 4),
        "hhi_new": round(hhi_new, 4),
    }


def _calc_hhi(weights_pct: list[float]) -> float:
    """Calcula Herfindahl-Hirschman Index a partir de pesos em %."""
    if not weights_pct:
        return 0.0
    w = np.array(weights_pct) / 100
    return float(np.sum(w**2))
