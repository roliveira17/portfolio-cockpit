"""Testes para analytics/performance.py."""

import numpy as np
import pandas as pd

from analytics.performance import (
    calc_beta_vs_benchmark,
    calc_cumulative_returns,
    calc_drawdown_series,
    calc_max_drawdown,
    calc_portfolio_returns,
    calc_sharpe_ratio,
    calc_sortino_ratio,
    calc_volatility,
)


def test_calc_portfolio_returns_equal_weights(sample_price_history):
    weights = {"AAA": 0.5, "BBB": 0.5}
    returns = calc_portfolio_returns(sample_price_history, weights)
    assert returns is not None
    assert len(returns) == 49  # pct_change drops first row
    assert returns.dtype == np.float64


def test_calc_portfolio_returns_single_ticker(sample_price_history):
    weights = {"AAA": 1.0}
    returns = calc_portfolio_returns(sample_price_history, weights)
    assert returns is not None
    expected = sample_price_history["AAA"].pct_change().dropna()
    pd.testing.assert_series_equal(returns, expected, check_names=False, atol=1e-10)


def test_calc_portfolio_returns_missing_ticker(sample_price_history):
    weights = {"XXX": 1.0}
    returns = calc_portfolio_returns(sample_price_history, weights)
    assert returns is None


def test_calc_portfolio_returns_none():
    assert calc_portfolio_returns(None, {"A": 0.5}) is None
    assert calc_portfolio_returns(pd.DataFrame(), {"A": 0.5}) is None


def test_calc_cumulative_returns(sample_returns):
    cum = calc_cumulative_returns(sample_returns)
    assert cum is not None
    assert len(cum) == len(sample_returns)
    assert cum.iloc[0] == 1 + sample_returns.iloc[0]


def test_calc_cumulative_returns_none():
    assert calc_cumulative_returns(None) is None
    assert calc_cumulative_returns(pd.Series(dtype=float)) is None


def test_calc_sharpe_ratio(sample_returns):
    sharpe = calc_sharpe_ratio(sample_returns, risk_free_annual=0.10)
    assert sharpe is not None
    assert isinstance(sharpe, float)


def test_calc_sharpe_ratio_edge_cases():
    assert calc_sharpe_ratio(None) is None
    assert calc_sharpe_ratio(pd.Series([0.01])) is None  # less than 2 elements
    # Constant returns → zero volatility → None
    assert calc_sharpe_ratio(pd.Series([0.01, 0.01, 0.01])) is None


def test_calc_sortino_ratio(sample_returns):
    sortino = calc_sortino_ratio(sample_returns, risk_free_annual=0.10)
    assert sortino is not None
    assert isinstance(sortino, float)


def test_calc_sortino_all_positive():
    # All positive returns → no downside → None
    returns = pd.Series([0.01, 0.02, 0.005, 0.015])
    assert calc_sortino_ratio(returns) is None


def test_calc_max_drawdown(sample_returns):
    dd = calc_max_drawdown(sample_returns)
    assert dd is not None
    assert dd < 0  # drawdown is negative
    # We inserted -5% and -8% drops, so max drawdown should be significant
    assert dd < -0.05


def test_calc_drawdown_series(sample_returns):
    dd = calc_drawdown_series(sample_returns)
    assert dd is not None
    assert len(dd) == len(sample_returns)
    assert (dd <= 0).all()  # all drawdown values <= 0


def test_calc_volatility(sample_returns):
    vol = calc_volatility(sample_returns, window=30)
    assert vol is not None
    assert vol > 0
    # Annualized volatility should be reasonable (1-100%)
    assert vol < 2.0


def test_calc_volatility_insufficient_data():
    short = pd.Series([0.01, 0.02])
    assert calc_volatility(short, window=30) is None


def test_calc_beta_vs_benchmark(sample_returns):
    # Portfolio = sample_returns, benchmark = slightly correlated series
    np.random.seed(99)
    benchmark = pd.Series(
        np.random.normal(0.0003, 0.012, len(sample_returns)),
        index=sample_returns.index,
    )
    beta = calc_beta_vs_benchmark(sample_returns, benchmark)
    assert beta is not None
    assert isinstance(beta, float)


def test_calc_beta_insufficient_data():
    short = pd.Series([0.01] * 5, index=pd.date_range("2025-01-01", periods=5))
    bench = pd.Series([0.02] * 5, index=pd.date_range("2025-01-01", periods=5))
    assert calc_beta_vs_benchmark(short, bench) is None


def test_calc_beta_none():
    assert calc_beta_vs_benchmark(None, pd.Series([0.01])) is None
    assert calc_beta_vs_benchmark(pd.Series([0.01]), None) is None
