"""Testes para analytics/risk.py."""

import pandas as pd

from analytics.risk import (
    calc_stress_scenario,
    calc_stress_test_portfolio,
    calc_var_historical,
    get_predefined_scenarios,
)


def test_calc_var_historical(sample_returns):
    var = calc_var_historical(sample_returns, confidence=0.95)
    assert var is not None
    assert var < 0  # VaR is a loss (negative)


def test_calc_var_historical_99(sample_returns):
    var_99 = calc_var_historical(sample_returns, confidence=0.99)
    var_95 = calc_var_historical(sample_returns, confidence=0.95)
    # 99% VaR should be more negative (worse) than 95%
    assert var_99 < var_95


def test_calc_var_insufficient_data():
    short = pd.Series([0.01] * 10)
    assert calc_var_historical(short) is None  # < 20 data points


def test_calc_var_none():
    assert calc_var_historical(None) is None


def test_calc_stress_test_portfolio(sample_portfolio_df):
    # AAA is in "financeiro" → has selic sensitivity in FACTOR_SENSITIVITIES
    # BBB is in "tech_semis" → may have usdbrl sensitivity
    # Use a simple shock
    shocks = {"selic_1pp": 1.0}
    result = calc_stress_test_portfolio(sample_portfolio_df, shocks)

    assert "total_impact_pct" in result
    assert "total_impact_brl" in result
    assert "new_total_brl" in result
    assert "per_position" in result
    assert len(result["per_position"]) == 3  # AAA, BBB, CAIXA


def test_calc_stress_test_zero_shock(sample_portfolio_df):
    shocks = {"selic_1pp": 0.0}
    result = calc_stress_test_portfolio(sample_portfolio_df, shocks)
    assert result["total_impact_pct"] == 0
    assert result["total_impact_brl"] == 0


def test_calc_stress_test_empty_df():
    empty = pd.DataFrame(columns=["ticker", "current_value_brl"])
    empty["current_value_brl"] = pd.to_numeric(empty["current_value_brl"])
    result = calc_stress_test_portfolio(empty, {"selic_1pp": 1.0})
    assert result["total_impact_pct"] == 0


def test_get_predefined_scenarios():
    scenarios = get_predefined_scenarios()
    assert len(scenarios) == 4
    assert "Estagflação" in scenarios
    assert "Risk-off Global" in scenarios
    assert "Selic Hawkish" in scenarios
    assert "Bull China" in scenarios

    # Each scenario should have all 4 factor keys
    for name, shocks in scenarios.items():
        assert "selic_1pp" in shocks
        assert "usdbrl_10pct" in shocks
        assert "brent_10pct" in shocks
        assert "ibov_10pct" in shocks


def test_calc_stress_scenario(sample_portfolio_df):
    # Fixture uses fake tickers (AAA, BBB) not in FACTOR_SENSITIVITIES,
    # so impact will be zero. Test validates the function runs without error
    # and returns the correct structure.
    result = calc_stress_scenario(sample_portfolio_df, "Estagflação")
    assert "total_impact_pct" in result
    assert "total_impact_brl" in result
    assert "per_position" in result


def test_calc_stress_scenario_unknown(sample_portfolio_df):
    result = calc_stress_scenario(sample_portfolio_df, "Cenário Inexistente")
    # Unknown scenario → empty shocks → zero impact
    assert result["total_impact_pct"] == 0


def test_calc_stress_test_real_ticker():
    """Test with a real ticker from FACTOR_SENSITIVITIES to verify non-zero impact."""
    df = pd.DataFrame([{
        "ticker": "INBR32",
        "current_value_brl": 10000.0,
    }])
    shocks = {"selic_1pp": 1.0}
    result = calc_stress_test_portfolio(df, shocks)
    assert result["total_impact_pct"] != 0
    assert result["total_impact_brl"] != 0
