"""Fixtures compartilhadas para testes de analytics, data e utils."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_portfolio_df() -> pd.DataFrame:
    """DataFrame de portfólio com valores conhecidos para testes."""
    return pd.DataFrame(
        [
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
        ]
    )


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


# ============================================================
# Fixtures para testes de data/ e utils/
# ============================================================


@pytest.fixture
def sample_brapi_response():
    """Resposta simulada da brapi.dev com 2 tickers."""
    return {
        "results": [
            {
                "symbol": "INBR32",
                "regularMarketPrice": 46.81,
                "regularMarketChangePercent": 2.1,
                "regularMarketChange": 0.96,
                "regularMarketVolume": 1500000,
                "regularMarketPreviousClose": 45.85,
                "marketCap": 30000000000,
            },
            {
                "symbol": "ENGI4",
                "regularMarketPrice": 10.00,
                "regularMarketChangePercent": -0.5,
                "regularMarketChange": -0.05,
                "regularMarketVolume": 800000,
                "regularMarketPreviousClose": 10.05,
                "marketCap": 12000000000,
            },
        ]
    }


@pytest.fixture
def sample_treasury_xml():
    """XML simulado do Treasury.gov com maturidades-chave."""
    return """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <entry>
    <content type="application/xml">
      <m:properties>
        <d:NEW_DATE>2026-02-20T00:00:00</d:NEW_DATE>
        <d:BC_1MONTH>4.10</d:BC_1MONTH>
        <d:BC_3MONTH>4.20</d:BC_3MONTH>
        <d:BC_6MONTH>4.15</d:BC_6MONTH>
        <d:BC_1YEAR>4.05</d:BC_1YEAR>
        <d:BC_2YEAR>4.00</d:BC_2YEAR>
        <d:BC_3YEAR>3.95</d:BC_3YEAR>
        <d:BC_5YEAR>4.10</d:BC_5YEAR>
        <d:BC_7YEAR>4.20</d:BC_7YEAR>
        <d:BC_10YEAR>4.25</d:BC_10YEAR>
        <d:BC_20YEAR>4.50</d:BC_20YEAR>
        <d:BC_30YEAR>4.45</d:BC_30YEAR>
      </m:properties>
    </content>
  </entry>
</feed>"""


@pytest.fixture
def mock_supabase_client():
    """Mock do Supabase client com chainable methods."""
    client = MagicMock()

    # Configurar chain padrão: .table().select().order().execute()
    mock_response = MagicMock()
    mock_response.data = []

    table_mock = MagicMock()
    client.table.return_value = table_mock

    # Todas as operações retornam o próprio mock (chainable)
    for method in ["select", "eq", "order", "limit", "insert", "update", "delete"]:
        getattr(table_mock, method).return_value = table_mock

    table_mock.execute.return_value = mock_response

    return client


@pytest.fixture
def sample_positions_data():
    """Lista de posições para testes de DB e portfolio."""
    return [
        {
            "id": "pos-1",
            "ticker": "INBR32",
            "company_name": "Inter & Co Inc.",
            "market": "BR",
            "currency": "BRL",
            "sector": "financeiro",
            "analyst": "Analista Financeiro",
            "quantity": 1905,
            "avg_price": 32.67,
            "total_invested": 62244.54,
            "dividends_received": 503.37,
            "target_weight": 15.0,
            "is_active": True,
        },
        {
            "id": "pos-2",
            "ticker": "NVDA",
            "company_name": "Nvidia",
            "market": "US",
            "currency": "USD",
            "sector": "tech_semis",
            "analyst": "Analista Tech",
            "quantity": 15.69,
            "avg_price": 191.23,
            "total_invested": 2999.99,
            "dividends_received": 0,
            "target_weight": 5.0,
            "is_active": True,
        },
    ]


@pytest.fixture
def sample_quotes():
    """Cotações simuladas para testes de portfolio."""
    return {
        "INBR32": {
            "price": 46.81,
            "change_pct": 2.1,
            "change_abs": 0.96,
            "volume": 1500000,
            "previous_close": 45.85,
            "market_cap": 30_000_000_000,
            "currency": "BRL",
            "source": "brapi",
        },
        "NVDA": {
            "price": 191.00,
            "change_pct": -0.12,
            "change_abs": -0.23,
            "volume": 50_000_000,
            "previous_close": 191.23,
            "market_cap": 4_700_000_000_000,
            "currency": "USD",
            "source": "yfinance",
        },
    }
