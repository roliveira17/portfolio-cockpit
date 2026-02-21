"""Testes estendidos para analytics/portfolio.py — funções não cobertas nos testes originais."""

from unittest.mock import patch

import pandas as pd
import pytest

from analytics.portfolio import (
    build_portfolio_df,
    calc_factor_exposure,
    calc_sector_allocation,
    calc_top_movers,
    calc_total_patrimony,
    calc_total_pnl,
)

# ============================================================
# build_portfolio_df
# ============================================================


class TestBuildPortfolioDf:
    @patch("analytics.portfolio.usd_to_brl", side_effect=lambda x: x * 5.75 if x else None)
    def test_basic_brl_position(self, mock_usd):
        positions = [
            {
                "ticker": "INBR32",
                "company_name": "Inter & Co",
                "sector": "financeiro",
                "market": "BR",
                "currency": "BRL",
                "analyst": "Analista 1",
                "quantity": 100,
                "avg_price": 30.0,
                "total_invested": 3000.0,
                "dividends_received": 100.0,
                "target_weight": 15.0,
            }
        ]
        quotes = {"INBR32": {"price": 35.0, "change_pct": 2.0}}
        df = build_portfolio_df(positions, quotes)
        assert len(df) == 1
        assert df.iloc[0]["current_price"] == 35.0
        assert df.iloc[0]["current_value_brl"] == 3500.0
        assert df.iloc[0]["pnl_abs"] == pytest.approx(500.0)
        assert df.iloc[0]["weight"] == 100.0  # only position

    @patch("analytics.portfolio.usd_to_brl", side_effect=lambda x: x * 5.75 if x else None)
    def test_usd_position_converted(self, mock_usd):
        positions = [
            {
                "ticker": "NVDA",
                "company_name": "Nvidia",
                "sector": "tech_semis",
                "market": "US",
                "currency": "USD",
                "analyst": "Analista 2",
                "quantity": 10,
                "avg_price": 190.0,
                "total_invested": 1900.0,
                "dividends_received": 0,
                "target_weight": 5.0,
            }
        ]
        quotes = {"NVDA": {"price": 200.0, "change_pct": 1.0}}
        df = build_portfolio_df(positions, quotes)
        assert df.iloc[0]["current_value_original"] == 2000.0
        assert df.iloc[0]["current_value_brl"] == pytest.approx(2000.0 * 5.75)

    @patch("analytics.portfolio.usd_to_brl", return_value=None)
    def test_missing_quote(self, mock_usd):
        positions = [
            {
                "ticker": "XXX",
                "company_name": "Sem Cotação",
                "sector": "caixa",
                "market": "BR",
                "currency": "BRL",
                "analyst": "",
                "quantity": 100,
                "avg_price": 10.0,
                "total_invested": 1000.0,
                "dividends_received": 0,
                "target_weight": 5.0,
            }
        ]
        quotes = {}
        df = build_portfolio_df(positions, quotes)
        assert df.iloc[0]["current_price"] is None
        assert df.iloc[0]["pnl_abs"] is None

    @patch("analytics.portfolio.usd_to_brl", return_value=None)
    def test_empty_positions_raises(self, mock_usd):
        """build_portfolio_df com lista vazia gera DataFrame sem colunas (KeyError)."""
        with pytest.raises(KeyError):
            build_portfolio_df([], {})


# ============================================================
# calc_total_patrimony
# ============================================================


class TestCalcTotalPatrimony:
    def test_sums_correctly(self, sample_portfolio_df):
        total = calc_total_patrimony(sample_portfolio_df)
        assert total == pytest.approx(4000.0)

    def test_empty_df(self):
        df = pd.DataFrame(columns=["current_value_brl"])
        assert calc_total_patrimony(df) == 0.0


# ============================================================
# calc_total_pnl
# ============================================================


class TestCalcTotalPnl:
    @patch("analytics.portfolio.usd_to_brl", side_effect=lambda x: x * 5.75 if x else None)
    def test_brl_only(self, mock_usd, sample_portfolio_df):
        pnl_abs, pnl_pct = calc_total_pnl(sample_portfolio_df)
        assert pnl_abs == pytest.approx(400.0)  # 200+200+0

    @patch("analytics.portfolio.usd_to_brl", side_effect=lambda x: x * 5.75 if x else None)
    def test_empty_df(self, mock_usd):
        df = pd.DataFrame(
            columns=["total_invested", "current_value_original", "currency"]
        )
        pnl_abs, pnl_pct = calc_total_pnl(df)
        assert pnl_abs == 0.0
        assert pnl_pct == 0.0


# ============================================================
# calc_sector_allocation
# ============================================================


class TestCalcSectorAllocation:
    def test_groups_by_sector(self, sample_portfolio_df):
        alloc = calc_sector_allocation(sample_portfolio_df)
        assert len(alloc) == 3  # financeiro, tech_semis, caixa
        assert "weight" in alloc.columns
        assert alloc["weight"].sum() == pytest.approx(100.0)

    def test_empty_df(self):
        df = pd.DataFrame(columns=["sector", "current_value_brl"])
        result = calc_sector_allocation(df)
        assert result.empty

    def test_sorted_by_weight_desc(self, sample_portfolio_df):
        alloc = calc_sector_allocation(sample_portfolio_df)
        weights = alloc["weight"].tolist()
        assert weights == sorted(weights, reverse=True)


# ============================================================
# calc_factor_exposure
# ============================================================


class TestCalcFactorExposure:
    def test_returns_all_factors(self, sample_portfolio_df):
        exposure = calc_factor_exposure(sample_portfolio_df)
        # Exposure dict should have keys for each factor
        assert isinstance(exposure, dict)

    def test_empty_df(self):
        df = pd.DataFrame(columns=["ticker", "current_value_brl"])
        result = calc_factor_exposure(df)
        assert result == {}

    def test_values_between_0_and_100(self, sample_portfolio_df):
        exposure = calc_factor_exposure(sample_portfolio_df)
        for val in exposure.values():
            assert 0 <= val <= 100


# ============================================================
# calc_top_movers
# ============================================================


class TestCalcTopMovers:
    def test_correct_order(self, sample_portfolio_df):
        gainers, losers = calc_top_movers(sample_portfolio_df)
        assert gainers.iloc[0]["ticker"] == "AAA"  # +1.5%
        assert losers.iloc[0]["ticker"] == "BBB"  # -0.5%

    def test_custom_n(self, sample_portfolio_df):
        gainers, losers = calc_top_movers(sample_portfolio_df, n=1)
        assert len(gainers) == 1
        assert len(losers) == 1

    def test_all_none_change_pct(self):
        df = pd.DataFrame(
            {"ticker": ["A", "B"], "change_pct": [None, None], "company_name": ["A", "B"]}
        )
        gainers, losers = calc_top_movers(df)
        assert gainers.empty
        assert losers.empty

    def test_empty_df(self):
        df = pd.DataFrame(columns=["ticker", "change_pct", "company_name"])
        gainers, losers = calc_top_movers(df)
        assert gainers.empty
        assert losers.empty
