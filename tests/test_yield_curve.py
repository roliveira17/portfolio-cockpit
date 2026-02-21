"""Testes para data/yield_curve.py — curvas de juros BR (pyettj) e US (Treasury XML)."""

import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


def _make_pyettj_mock(return_df):
    """Create pyettj module mocks properly chained."""
    mock_ettj = MagicMock()
    mock_ettj.get_ettj = MagicMock(return_value=return_df)

    mock_pyettj = MagicMock()
    mock_pyettj.ettj = mock_ettj

    return mock_pyettj, mock_ettj


# ============================================================
# fetch_br_yield_curve
# ============================================================


class TestFetchBrYieldCurve:
    def _call_with_mock(self, return_df, ref_date=None):
        """Helper: reload yield_curve module with mocked pyettj and call function."""
        mock_pyettj, mock_ettj = _make_pyettj_mock(return_df)

        with patch.dict(sys.modules, {"pyettj": mock_pyettj, "pyettj.ettj": mock_ettj}):
            with patch("data.yield_curve.st"):
                import importlib

                import data.yield_curve

                importlib.reload(data.yield_curve)
                if ref_date:
                    return data.yield_curve.fetch_br_yield_curve.__wrapped__(ref_date)
                return data.yield_curve.fetch_br_yield_curve.__wrapped__()

    def test_success(self):
        mock_df = pd.DataFrame(
            {
                "dias_corridos": [21, 63, 126, 252, 504],
                "taxa": [13.50, 14.00, 14.25, 14.50, 14.20],
            }
        )
        result = self._call_with_mock(mock_df, "21/02/2026")

        assert result is not None
        assert "dias_corridos" in result.columns
        assert "taxa" in result.columns
        assert "anos" in result.columns
        assert len(result) == 5

    def test_pyettj_returns_none(self):
        result = self._call_with_mock(None)
        assert result is None

    def test_pyettj_empty_df(self):
        result = self._call_with_mock(pd.DataFrame())
        assert result is None

    def test_anos_calculated_correctly(self):
        mock_df = pd.DataFrame(
            {
                "dias_corridos": [252],
                "taxa": [14.50],
            }
        )
        result = self._call_with_mock(mock_df)

        assert result is not None
        assert result.iloc[0]["anos"] == pytest.approx(1.0)

    def test_column_normalization(self):
        """Test that different column names from pyettj are normalized."""
        mock_df = pd.DataFrame(
            {
                "Dias Corridos": [21, 63],
                "Taxa (% a.a.)": [13.50, 14.00],
            }
        )
        result = self._call_with_mock(mock_df)

        assert result is not None
        assert "dias_corridos" in result.columns
        assert "taxa" in result.columns


# ============================================================
# fetch_us_treasury_curve
# ============================================================


class TestFetchUsTreasuryCurve:
    @patch("data.yield_curve.requests.get")
    @patch("data.yield_curve.st")
    def test_success(self, mock_st, mock_get, sample_treasury_xml):
        mock_resp = MagicMock()
        mock_resp.content = sample_treasury_xml.encode("utf-8")
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from data.yield_curve import fetch_us_treasury_curve

        result = fetch_us_treasury_curve.__wrapped__(2026)

        assert result is not None
        assert "label" in result.columns
        assert "years" in result.columns
        assert "yield_pct" in result.columns
        assert len(result) == 11

    @patch("data.yield_curve.requests.get")
    @patch("data.yield_curve.st")
    def test_10year_value(self, mock_st, mock_get, sample_treasury_xml):
        mock_resp = MagicMock()
        mock_resp.content = sample_treasury_xml.encode("utf-8")
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from data.yield_curve import fetch_us_treasury_curve

        result = fetch_us_treasury_curve.__wrapped__(2026)

        row_10y = result[result["label"] == "10A"]
        assert row_10y.iloc[0]["yield_pct"] == pytest.approx(4.25)

    @patch("data.yield_curve.requests.get", side_effect=Exception("timeout"))
    @patch("data.yield_curve.st")
    def test_failure_returns_none(self, mock_st, mock_get):
        from data.yield_curve import fetch_us_treasury_curve

        result = fetch_us_treasury_curve.__wrapped__(2026)
        assert result is None

    @patch("data.yield_curve.requests.get")
    @patch("data.yield_curve.st")
    def test_empty_xml_returns_none(self, mock_st, mock_get):
        mock_resp = MagicMock()
        mock_resp.content = b"""<?xml version="1.0"?><feed></feed>"""
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from data.yield_curve import fetch_us_treasury_curve

        result = fetch_us_treasury_curve.__wrapped__(2026)
        assert result is None
