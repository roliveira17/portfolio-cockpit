"""Testes para data/global_markets.py — índices globais e commodities com mocks."""

from unittest.mock import MagicMock, patch

# ============================================================
# fetch_global_indices
# ============================================================


class TestFetchGlobalIndices:
    @patch("data.global_markets.yf.Ticker")
    @patch("data.global_markets.st")
    def test_returns_all_regions(self, mock_st, mock_ticker):
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda k: {
            "lastPrice": 6100.0, "previousClose": 6050.0
        }.get(k)
        mock_ticker.return_value.fast_info = mock_info

        from data.global_markets import fetch_global_indices

        result = fetch_global_indices.__wrapped__()
        assert "americas" in result
        assert "europe" in result
        assert "asia_pacific" in result
        assert len(result["americas"]) > 0

    @patch("data.global_markets.yf.Ticker")
    @patch("data.global_markets.st")
    def test_index_has_required_fields(self, mock_st, mock_ticker):
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda k: {
            "lastPrice": 6100.0, "previousClose": 6050.0
        }.get(k)
        mock_ticker.return_value.fast_info = mock_info

        from data.global_markets import fetch_global_indices

        result = fetch_global_indices.__wrapped__()
        entry = result["americas"][0]
        assert "name" in entry
        assert "country" in entry
        assert "ticker" in entry
        assert "price" in entry
        assert "change_pct" in entry

    @patch("data.global_markets.yf.Ticker", side_effect=Exception("yf down"))
    @patch("data.global_markets.st")
    def test_failure_returns_none_price(self, mock_st, mock_ticker):
        from data.global_markets import fetch_global_indices

        result = fetch_global_indices.__wrapped__()
        for region_data in result.values():
            for entry in region_data:
                assert entry["price"] is None
                assert entry["change_pct"] is None


# ============================================================
# fetch_commodities
# ============================================================


class TestFetchCommodities:
    @patch("data.global_markets.yf.Ticker")
    @patch("data.global_markets.st")
    def test_returns_list(self, mock_st, mock_ticker):
        mock_info = MagicMock()
        mock_info.get.side_effect = lambda k: {
            "lastPrice": 74.2, "previousClose": 75.0
        }.get(k)
        mock_ticker.return_value.fast_info = mock_info

        from data.global_markets import fetch_commodities

        result = fetch_commodities.__wrapped__()
        assert isinstance(result, list)
        assert len(result) == 8  # 8 commodities in constants

    @patch("data.global_markets.yf.Ticker", side_effect=Exception("yf down"))
    @patch("data.global_markets.st")
    def test_failure_graceful(self, mock_st, mock_ticker):
        from data.global_markets import fetch_commodities

        result = fetch_commodities.__wrapped__()
        assert len(result) == 8
        for entry in result:
            assert entry["price"] is None
