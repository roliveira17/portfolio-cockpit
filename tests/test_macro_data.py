"""Testes para data/macro_data.py — indicadores macro BCB + yfinance com mocks."""

from unittest.mock import MagicMock, patch

import pytest

from data.macro_data import _extract_value, fetch_macro_snapshot

# ============================================================
# _extract_value (pura)
# ============================================================


class TestExtractValue:
    def test_normal(self):
        assert _extract_value({"value": 128450.0, "change_pct": 1.2}) == 128450.0

    def test_none_input(self):
        assert _extract_value(None) is None

    def test_missing_key(self):
        assert _extract_value({"change_pct": 1.2}) is None


# ============================================================
# fetch_bcb_indicator
# ============================================================


class TestFetchBcbIndicator:
    @patch("data.macro_data.requests.get")
    @patch("data.macro_data.st")
    def test_returns_float(self, mock_st, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"valor": "13,25"}]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from data.macro_data import fetch_bcb_indicator

        result = fetch_bcb_indicator.__wrapped__(432)
        assert result == pytest.approx(13.25)

    @patch("data.macro_data.requests.get", side_effect=Exception("timeout"))
    @patch("data.macro_data.st")
    def test_failure_returns_none(self, mock_st, mock_get):
        from data.macro_data import fetch_bcb_indicator

        result = fetch_bcb_indicator.__wrapped__(432)
        assert result is None

    @patch("data.macro_data.requests.get")
    @patch("data.macro_data.st")
    def test_empty_response_returns_none(self, mock_st, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from data.macro_data import fetch_bcb_indicator

        result = fetch_bcb_indicator.__wrapped__(432)
        assert result is None


# ============================================================
# fetch_macro_global
# ============================================================


class TestFetchMacroGlobal:
    @patch("data.macro_data.yf.Ticker")
    @patch("data.macro_data.st")
    def test_returns_all_indicators(self, mock_st, mock_ticker):
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda k: {"lastPrice": 6100.0, "previousClose": 6050.0}.get(k)
        mock_ticker.return_value.fast_info = mock_info

        from data.macro_data import fetch_macro_global

        result = fetch_macro_global.__wrapped__()
        assert "sp500" in result
        assert "vix" in result
        assert result["sp500"]["value"] == 6100.0
        assert result["sp500"]["change_pct"] is not None

    @patch("data.macro_data.yf.Ticker", side_effect=Exception("yfinance down"))
    @patch("data.macro_data.st")
    def test_failure_returns_none_entries(self, mock_st, mock_ticker):
        from data.macro_data import fetch_macro_global

        result = fetch_macro_global.__wrapped__()
        for val in result.values():
            assert val is None


# ============================================================
# fetch_macro_snapshot
# ============================================================


class TestFetchMacroSnapshot:
    @patch("data.macro_data.fetch_macro_global")
    @patch("data.macro_data.fetch_macro_br")
    def test_consolidates_all(self, mock_br, mock_global):
        mock_br.return_value = {
            "selic": 13.25,
            "ipca_12m": 4.56,
            "cdi": 13.15,
            "usd_brl": 5.75,
        }
        mock_global.return_value = {
            "sp500": {"value": 6100.0, "change_pct": 0.8},
            "vix": {"value": 15.2, "change_pct": -0.5},
            "dxy": {"value": 106.8, "change_pct": -0.2},
            "brent": {"value": 74.2, "change_pct": -1.1},
            "treasury_10y": {"value": 4.25, "change_pct": 0.1},
            "ibov": {"value": 128450.0, "change_pct": 1.2},
        }
        result = fetch_macro_snapshot()
        assert result["selic"] == 13.25
        assert result["sp500"] == 6100.0
        assert result["vix"] == 15.2

    @patch("data.macro_data.fetch_macro_global")
    @patch("data.macro_data.fetch_macro_br")
    def test_handles_none_gracefully(self, mock_br, mock_global):
        mock_br.return_value = {"selic": None, "ipca_12m": None, "cdi": None, "usd_brl": None}
        mock_global.return_value = {
            "sp500": None,
            "vix": None,
            "dxy": None,
            "brent": None,
            "treasury_10y": None,
            "ibov": None,
        }
        result = fetch_macro_snapshot()
        assert result["selic"] is None
        assert result["sp500"] is None
