"""Testes para data/market_data.py — cotacoes BR (brapi) e US (yfinance) com mocks."""

from unittest.mock import MagicMock, patch

import pytest

from data.market_data import (
    _calc_change_abs,
    _calc_change_pct,
    _fetch_brapi,
    _fetch_yfinance,
    _fetch_yfinance_br,
    fetch_all_quotes,
    fetch_fundamentals,
)

# ============================================================
# _calc_change_pct
# ============================================================


class TestCalcChangePct:
    def test_normal(self):
        assert _calc_change_pct(105.0, 100.0) == pytest.approx(5.0)

    def test_negative(self):
        assert _calc_change_pct(95.0, 100.0) == pytest.approx(-5.0)

    def test_none_current(self):
        assert _calc_change_pct(None, 100.0) is None

    def test_none_previous(self):
        assert _calc_change_pct(100.0, None) is None

    def test_zero_previous(self):
        assert _calc_change_pct(100.0, 0) is None


# ============================================================
# _calc_change_abs
# ============================================================


class TestCalcChangeAbs:
    def test_normal(self):
        assert _calc_change_abs(105.0, 100.0) == pytest.approx(5.0)

    def test_negative(self):
        assert _calc_change_abs(95.0, 100.0) == pytest.approx(-5.0)

    def test_none_current(self):
        assert _calc_change_abs(None, 100.0) is None

    def test_none_previous(self):
        assert _calc_change_abs(100.0, None) is None


# ============================================================
# _fetch_brapi
# ============================================================


class TestFetchBrapi:
    @patch("data.market_data.requests.get")
    @patch("data.market_data.st")
    def test_success(self, mock_st, mock_get, sample_brapi_response):
        mock_st.secrets = {"brapi": {"token": "test-token"}}
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_brapi_response
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _fetch_brapi(["INBR32", "ENGI4"])
        assert "INBR32" in result
        assert result["INBR32"]["price"] == 46.81
        assert result["INBR32"]["currency"] == "BRL"
        assert result["INBR32"]["source"] == "brapi"

    @patch("data.market_data.requests.get")
    @patch("data.market_data.st")
    def test_empty_results(self, mock_st, mock_get):
        mock_st.secrets = {"brapi": {"token": ""}}
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"results": []}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = _fetch_brapi(["XXX"])
        assert result == {}

    @patch("data.market_data.requests.get", side_effect=Exception("timeout"))
    @patch("data.market_data.st")
    def test_raises_on_failure(self, mock_st, mock_get):
        mock_st.secrets = {"brapi": {"token": ""}}
        with pytest.raises(Exception):
            _fetch_brapi(["INBR32"])


# ============================================================
# _fetch_yfinance
# ============================================================


class TestFetchYfinance:
    @patch("data.market_data.yf.Tickers")
    def test_success(self, mock_tickers):
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda k: {
            "lastPrice": 191.0,
            "previousClose": 190.0,
            "lastVolume": 50000000,
            "marketCap": 4700000000000,
        }.get(k)

        ticker_mock = MagicMock()
        ticker_mock.fast_info = mock_info
        mock_tickers.return_value.tickers = {"NVDA": ticker_mock}

        result = _fetch_yfinance(["NVDA"], currency="USD")
        assert "NVDA" in result
        assert result["NVDA"]["price"] == 191.0
        assert result["NVDA"]["currency"] == "USD"
        assert result["NVDA"]["source"] == "yfinance"

    @patch("data.market_data.yf.Tickers")
    def test_ticker_failure_skipped(self, mock_tickers):
        ticker_mock = MagicMock()
        ticker_mock.fast_info.__getitem__ = MagicMock(side_effect=Exception("no data"))
        ticker_mock.fast_info.get = MagicMock(side_effect=Exception("no data"))
        mock_tickers.return_value.tickers = {"INVALID": ticker_mock}

        result = _fetch_yfinance(["INVALID"])
        assert result == {}

    def test_empty_tickers(self):
        result = _fetch_yfinance([])
        assert result == {}


# ============================================================
# _fetch_yfinance_br
# ============================================================


class TestFetchYfinanceBr:
    @patch("data.market_data._fetch_yfinance")
    def test_adds_sa_suffix(self, mock_yf):
        mock_yf.return_value = {"INBR32": {"price": 46.0, "source": "yfinance"}}
        _fetch_yfinance_br(["INBR32"])
        # Verify it was called with .SA suffix and original tickers
        mock_yf.assert_called_once_with(["INBR32.SA"], original_tickers=["INBR32"], currency="BRL")


# ============================================================
# fetch_all_quotes
# ============================================================


class TestFetchAllQuotes:
    @patch("data.market_data.fetch_quotes_us")
    @patch("data.market_data.fetch_quotes_br")
    def test_combines_br_and_us(self, mock_br, mock_us):
        mock_br.return_value = {"INBR32": {"price": 46.81}}
        mock_us.return_value = {"NVDA": {"price": 191.0}}
        result = fetch_all_quotes()
        assert "INBR32" in result
        assert "NVDA" in result


# ============================================================
# fetch_fundamentals
# ============================================================


def _make_yf_info(overrides: dict | None = None) -> dict:
    """Helper: cria dict .info padrao com campos fundamentais."""
    base = {
        "trailingPE": 45.2,
        "forwardPE": 30.1,
        "priceToBook": 38.5,
        "enterpriseToEbitda": 35.2,
        "trailingAnnualDividendYield": 0.003,
        "revenueGrowth": 0.94,
        "profitMargins": 0.55,
        "returnOnEquity": 1.15,
        "debtToEquity": 17.2,
    }
    if overrides:
        base.update(overrides)
    return base


class TestFetchFundamentals:
    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_us_stock(self, mock_st, mock_ticker):
        mock_ticker.return_value.info = _make_yf_info()

        result = fetch_fundamentals.__wrapped__([], ["NVDA"])

        assert "NVDA" in result
        assert result["NVDA"]["trailing_pe"] == 45.2
        assert result["NVDA"]["roe"] == 1.15
        assert result["NVDA"]["ev_ebitda"] == 35.2

    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_br_stock_sa_suffix(self, mock_st, mock_ticker):
        mock_ticker.return_value.info = _make_yf_info({"trailingPE": 8.1})

        result = fetch_fundamentals.__wrapped__(["SUZB3"], [])

        assert "SUZB3" in result
        assert result["SUZB3"]["trailing_pe"] == 8.1
        # Verifica que foi chamado com .SA
        mock_ticker.assert_called_with("SUZB3.SA")

    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_missing_fields_returns_none(self, mock_st, mock_ticker):
        partial_info = {
            "trailingPE": 12.0,
            "priceToBook": 2.5,
        }
        mock_ticker.return_value.info = partial_info

        result = fetch_fundamentals.__wrapped__(["ENGI4"], [])

        assert "ENGI4" in result
        assert result["ENGI4"]["trailing_pe"] == 12.0
        assert result["ENGI4"]["forward_pe"] is None
        assert result["ENGI4"]["ev_ebitda"] is None

    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_excludes_special_tickers(self, mock_st, mock_ticker):
        mock_ticker.return_value.info = _make_yf_info()

        result = fetch_fundamentals.__wrapped__(["CAIXA", "FIDC_MICROCREDITO"], ["EWY"])

        assert "CAIXA" not in result
        assert "FIDC_MICROCREDITO" not in result
        assert "EWY" not in result
        mock_ticker.assert_not_called()

    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_api_error_skips_ticker(self, mock_st, mock_ticker):
        mock_ticker.return_value.info.__getitem__ = MagicMock(side_effect=Exception("API error"))
        mock_ticker.side_effect = Exception("connection failed")

        result = fetch_fundamentals.__wrapped__([], ["NVDA"])

        assert result == {}

    @patch("data.market_data.st")
    def test_empty_input(self, mock_st):
        result = fetch_fundamentals.__wrapped__([], [])
        assert result == {}

    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_mixed_br_us(self, mock_st, mock_ticker):
        call_count = [0]

        def side_effect(symbol):
            call_count[0] += 1
            mock_obj = MagicMock()
            if symbol == "NVDA":
                mock_obj.info = _make_yf_info({"trailingPE": 45.0})
            else:
                mock_obj.info = _make_yf_info({"trailingPE": 8.0})
            return mock_obj

        mock_ticker.side_effect = side_effect

        result = fetch_fundamentals.__wrapped__(["SUZB3"], ["NVDA"])

        assert "SUZB3" in result
        assert "NVDA" in result
        assert result["SUZB3"]["trailing_pe"] == 8.0
        assert result["NVDA"]["trailing_pe"] == 45.0

    @patch("data.market_data.yf.Ticker")
    @patch("data.market_data.st")
    def test_dividend_yield_range(self, mock_st, mock_ticker):
        mock_ticker.return_value.info = _make_yf_info({"trailingAnnualDividendYield": 0.065})

        result = fetch_fundamentals.__wrapped__([], ["TSM"])

        assert result["TSM"]["dividend_yield"] == pytest.approx(0.065)
        assert 0 <= result["TSM"]["dividend_yield"] <= 1.0
