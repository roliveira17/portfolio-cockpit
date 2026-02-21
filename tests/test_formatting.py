"""Testes para utils/formatting.py — funções puras de formatação."""

from datetime import date, datetime

from utils.formatting import fmt_brl, fmt_date, fmt_delta, fmt_number, fmt_pct, fmt_usd

# ============================================================
# fmt_brl
# ============================================================


class TestFmtBrl:
    def test_positive_value(self):
        assert fmt_brl(1234.56) == "R$1.234,56"

    def test_negative_value(self):
        assert fmt_brl(-500.00) == "R$-500,00"

    def test_zero(self):
        assert fmt_brl(0) == "R$0,00"

    def test_none_returns_dash(self):
        assert fmt_brl(None) == "—"

    def test_compact_thousands(self):
        assert fmt_brl(514000, compact=True) == "R$514.0k"

    def test_compact_millions(self):
        assert fmt_brl(2500000, compact=True) == "R$2.5M"

    def test_compact_small_value(self):
        # Below 1000, no compacting
        assert fmt_brl(999.99, compact=True) == "R$999,99"

    def test_large_value(self):
        result = fmt_brl(1234567.89)
        assert result == "R$1.234.567,89"

    def test_compact_negative_millions(self):
        assert fmt_brl(-1500000, compact=True) == "R$-1.5M"


# ============================================================
# fmt_usd
# ============================================================


class TestFmtUsd:
    def test_positive_value(self):
        assert fmt_usd(13500.00) == "US$13,500.00"

    def test_negative_value(self):
        assert fmt_usd(-250.50) == "US$-250.50"

    def test_zero(self):
        assert fmt_usd(0) == "US$0.00"

    def test_none_returns_dash(self):
        assert fmt_usd(None) == "—"

    def test_compact_thousands(self):
        assert fmt_usd(13500, compact=True) == "US$13.5k"

    def test_compact_millions(self):
        assert fmt_usd(2500000, compact=True) == "US$2.5M"

    def test_compact_small(self):
        assert fmt_usd(500, compact=True) == "US$500.00"


# ============================================================
# fmt_pct
# ============================================================


class TestFmtPct:
    def test_positive(self):
        assert fmt_pct(14.3) == "14.3%"

    def test_negative(self):
        assert fmt_pct(-2.5) == "-2.5%"

    def test_zero(self):
        assert fmt_pct(0.0) == "0.0%"

    def test_none_returns_dash(self):
        assert fmt_pct(None) == "—"

    def test_with_sign_positive(self):
        assert fmt_pct(14.3, sign=True) == "+14.3%"

    def test_with_sign_negative(self):
        assert fmt_pct(-2.5, sign=True) == "-2.5%"

    def test_with_sign_zero(self):
        assert fmt_pct(0.0, sign=True) == "0.0%"

    def test_custom_decimals(self):
        assert fmt_pct(3.1415, decimals=2) == "3.14%"


# ============================================================
# fmt_number
# ============================================================


class TestFmtNumber:
    def test_integer(self):
        assert fmt_number(128450.0, decimals=0) == "128.450"

    def test_decimal(self):
        assert fmt_number(128450.5) == "128.450,50"

    def test_none_returns_dash(self):
        assert fmt_number(None) == "—"

    def test_large_number(self):
        assert fmt_number(1234567.89) == "1.234.567,89"

    def test_small_number(self):
        assert fmt_number(0.5) == "0,50"


# ============================================================
# fmt_date
# ============================================================


class TestFmtDate:
    def test_date_object(self):
        assert fmt_date(date(2026, 2, 18)) == "18/02/2026"

    def test_datetime_object(self):
        assert fmt_date(datetime(2026, 2, 18, 10, 30)) == "18/02/2026"

    def test_iso_string(self):
        assert fmt_date("2026-02-18") == "18/02/2026"

    def test_short_format(self):
        assert fmt_date(date(2026, 2, 18), short=True) == "18/02"

    def test_none_returns_dash(self):
        assert fmt_date(None) == "—"


# ============================================================
# fmt_delta
# ============================================================


class TestFmtDelta:
    def test_positive(self):
        assert fmt_delta(1.5) == "↑ +1.5%"

    def test_negative(self):
        assert fmt_delta(-0.3) == "↓ -0.3%"

    def test_zero(self):
        assert fmt_delta(0.0) == "→ 0.0%"

    def test_none_returns_dash(self):
        assert fmt_delta(None) == "—"

    def test_large_positive(self):
        assert fmt_delta(10.0) == "↑ +10.0%"

    def test_large_negative(self):
        assert fmt_delta(-15.3) == "↓ -15.3%"
