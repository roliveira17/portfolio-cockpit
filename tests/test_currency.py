"""Testes para utils/currency.py — conversão BRL ↔ USD via PTAX."""

from unittest.mock import MagicMock, patch

import pytest

# ============================================================
# get_ptax
# ============================================================


class TestGetPtax:
    @patch("utils.currency.requests.get")
    @patch("utils.currency.st")
    def test_returns_ptax_from_bcb(self, mock_st, mock_get):
        """BCB retorna PTAX corretamente."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"valor": "5,75"}]
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        # Importar após patches ativas
        from utils.currency import get_ptax

        # Bypass cache: chamar a função wrapped
        result = get_ptax.__wrapped__()
        assert result == 5.75

    @patch("utils.currency.requests.get", side_effect=Exception("timeout"))
    @patch("utils.currency.st")
    def test_fallback_on_bcb_failure(self, mock_st, mock_get):
        """BCB indisponível → retorna fallback 5.75."""
        from utils.currency import get_ptax

        result = get_ptax.__wrapped__()
        assert result == 5.75

    @patch("utils.currency.requests.get")
    @patch("utils.currency.st")
    def test_empty_bcb_response(self, mock_st, mock_get):
        """BCB retorna lista vazia → fallback."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from utils.currency import get_ptax

        result = get_ptax.__wrapped__()
        assert result == 5.75


# ============================================================
# brl_to_usd
# ============================================================


class TestBrlToUsd:
    @patch("utils.currency.get_ptax", return_value=5.75)
    def test_positive_value(self, mock_ptax):
        from utils.currency import brl_to_usd

        result = brl_to_usd(575.0)
        assert result == pytest.approx(100.0)

    @patch("utils.currency.get_ptax", return_value=5.75)
    def test_zero(self, mock_ptax):
        from utils.currency import brl_to_usd

        assert brl_to_usd(0.0) == 0.0

    def test_none_returns_none(self):
        from utils.currency import brl_to_usd

        assert brl_to_usd(None) is None


# ============================================================
# usd_to_brl
# ============================================================


class TestUsdToBrl:
    @patch("utils.currency.get_ptax", return_value=5.75)
    def test_positive_value(self, mock_ptax):
        from utils.currency import usd_to_brl

        result = usd_to_brl(100.0)
        assert result == pytest.approx(575.0)

    @patch("utils.currency.get_ptax", return_value=5.75)
    def test_zero(self, mock_ptax):
        from utils.currency import usd_to_brl

        assert usd_to_brl(0.0) == 0.0

    def test_none_returns_none(self):
        from utils.currency import usd_to_brl

        assert usd_to_brl(None) is None


# ============================================================
# Roundtrip consistency
# ============================================================


class TestRoundtrip:
    @patch("utils.currency.get_ptax", return_value=5.75)
    def test_brl_usd_brl_roundtrip(self, mock_ptax):
        from utils.currency import brl_to_usd, usd_to_brl

        original = 1000.0
        result = usd_to_brl(brl_to_usd(original))
        assert result == pytest.approx(original)

    @patch("utils.currency.get_ptax", return_value=5.75)
    def test_usd_brl_usd_roundtrip(self, mock_ptax):
        from utils.currency import brl_to_usd, usd_to_brl

        original = 200.0
        result = brl_to_usd(usd_to_brl(original))
        assert result == pytest.approx(original)
