"""Fixtures compartilhadas para testes de analytics."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_portfolio_df() -> pd.DataFrame:
    """DataFrame de portfólio com valores conhecidos para testes."""
    return pd.DataFrame([
        {
            "ticker": "AAA",
            "company_name": "Empresa AAA",
            "sector": "financeiro",
            "market": "BR",
            "currency": "BRL",
            "analyst": "Analista 1",
            "quantity": 100,
            "avg_price": 10.0,
            "total_invested": 1000.0,
            "dividends_received": 0,
            "current_price": 12.0,
            "current_value_original": 1200.0,
            "current_value_brl": 1200.0,
            "pnl_abs": 200.0,
            "pnl_pct": 20.0,
            "pnl_with_div_pct": 20.0,
            "weight": 30.0,
            "target_weight": 25.0,
            "weight_gap": 5.0,
            "change_pct": 1.5,
        },
        {
            "ticker": "BBB",
            "company_name": "Empresa BBB",
            "sector": "tech_semis",
            "market": "BR",
            "currency": "BRL",
            "analyst": "Analista 2",
            "quantity": 200,
            "avg_price": 5.0,
            "total_invested": 1000.0,
            "dividends_received": 0,
            "current_price": 6.0,
            "current_value_original": 1200.0,
            "current_value_brl": 1200.0,
            "pnl_abs": 200.0,
            "pnl_pct": 20.0,
            "pnl_with_div_pct": 20.0,
            "weight": 30.0,
            "target_weight": 35.0,
            "weight_gap": -5.0,
            "change_pct": -0.5,
        },
        {
            "ticker": "CAIXA",
            "company_name": "Caixa",
            "sector": "caixa",
            "market": "BR",
            "currency": "BRL",
            "analyst": "",
            "quantity": 1,
            "avg_price": 1600.0,
            "total_invested": 1600.0,
            "dividends_received": 0,
            "current_price": 1600.0,
            "current_value_original": 1600.0,
            "current_value_brl": 1600.0,
            "pnl_abs": 0,
            "pnl_pct": 0,
            "pnl_with_div_pct": 0,
            "weight": 40.0,
            "target_weight": 40.0,
            "weight_gap": 0,
            "change_pct": 0,
        },
    ])


@pytest.fixture
def sample_price_history() -> pd.DataFrame:
    """Histórico de preços com retornos conhecidos (50 dias, 2 tickers)."""
    np.random.seed(42)
    dates = pd.date_range("2025-11-01", periods=50, freq="B")
    # AAA: preço base 100, retornos pequenos positivos
    aaa_returns = np.random.normal(0.001, 0.02, 50)
    aaa_prices = 100 * np.cumprod(1 + aaa_returns)
    # BBB: preço base 50, retornos negativos (para gerar drawdown)
    bbb_returns = np.random.normal(-0.001, 0.015, 50)
    bbb_prices = 50 * np.cumprod(1 + bbb_returns)
    return pd.DataFrame({"AAA": aaa_prices, "BBB": bbb_prices}, index=dates)


@pytest.fixture
def sample_returns() -> pd.Series:
    """Série de retornos diários com propriedades conhecidas (50 dias)."""
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.015, 50)
    # Inserir um drawdown claro
    returns[20] = -0.05  # queda de 5% no dia 20
    returns[21] = -0.08  # queda de 8% no dia 21
    return pd.Series(returns, index=pd.date_range("2025-11-01", periods=50, freq="B"))
