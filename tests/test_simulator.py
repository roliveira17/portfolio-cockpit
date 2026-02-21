"""Testes para analytics/simulator.py."""

import pandas as pd

from analytics.simulator import _calc_hhi, simulate_new_trade, simulate_rebalance


def test_calc_hhi_equal_weights():
    # 4 posições iguais de 25% cada → HHI = 4 * (0.25)^2 = 0.25
    hhi = _calc_hhi([25.0, 25.0, 25.0, 25.0])
    assert abs(hhi - 0.25) < 0.001


def test_calc_hhi_concentrated():
    # 1 posição de 100% → HHI = 1.0
    hhi = _calc_hhi([100.0])
    assert abs(hhi - 1.0) < 0.001


def test_calc_hhi_empty():
    assert _calc_hhi([]) == 0.0


def test_calc_hhi_realistic():
    # Pesos típicos: 30, 30, 40
    hhi = _calc_hhi([30.0, 30.0, 40.0])
    expected = 0.30**2 + 0.30**2 + 0.40**2  # 0.09 + 0.09 + 0.16 = 0.34
    assert abs(hhi - expected) < 0.001


def test_simulate_rebalance_no_change(sample_portfolio_df):
    # Manter pesos atuais → nenhum trade
    current_weights = {row["ticker"]: float(row["weight"]) for _, row in sample_portfolio_df.iterrows()}
    result = simulate_rebalance(sample_portfolio_df, current_weights)
    assert result["trades"] == []
    assert result["hhi_old"] == result["hhi_new"]


def test_simulate_rebalance_has_trades(sample_portfolio_df):
    # Mudar peso de AAA de 30% para 20%
    new_weights = {"AAA": 20.0, "BBB": 40.0, "CAIXA": 40.0}
    result = simulate_rebalance(sample_portfolio_df, new_weights)

    assert len(result["trades"]) > 0
    assert "hhi_old" in result
    assert "hhi_new" in result
    assert "exposure_old" in result
    assert "exposure_new" in result

    # Verificar que trades têm estrutura correta
    for trade in result["trades"]:
        assert "ticker" in trade
        assert "action" in trade
        assert trade["action"] in ("COMPRAR", "VENDER")
        assert "quantity" in trade
        assert "value_brl" in trade


def test_simulate_rebalance_empty_df():
    empty = pd.DataFrame(
        columns=[
            "ticker",
            "weight",
            "target_weight",
            "current_price",
            "current_value_brl",
            "currency",
            "sector",
        ]
    )
    empty["current_value_brl"] = pd.to_numeric(empty["current_value_brl"])
    result = simulate_rebalance(empty, {})
    assert result["trades"] == []


def test_simulate_new_trade_buy(sample_portfolio_df):
    result = simulate_new_trade(
        sample_portfolio_df,
        "AAA",
        "COMPRAR",
        50,
        12.0,
    )
    assert result is not None
    assert result["new_weight"] > result["old_weight"]
    assert result["new_cash"] < result["old_cash"]
    assert result["cash_impact_brl"] < 0  # compra reduz caixa


def test_simulate_new_trade_sell(sample_portfolio_df):
    result = simulate_new_trade(
        sample_portfolio_df,
        "AAA",
        "VENDER",
        50,
        12.0,
    )
    assert result is not None
    assert result["new_weight"] < result["old_weight"]
    assert result["new_cash"] > result["old_cash"]
    assert result["cash_impact_brl"] > 0  # venda aumenta caixa


def test_simulate_new_trade_hhi_changes(sample_portfolio_df):
    result = simulate_new_trade(
        sample_portfolio_df,
        "AAA",
        "COMPRAR",
        100,
        12.0,
    )
    # Comprar mais AAA (já grande) deve aumentar concentração
    assert result["hhi_new"] >= result["hhi_old"]
