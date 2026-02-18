"""Funções de formatação: moedas, percentuais, datas."""

from datetime import date, datetime


def fmt_brl(value: float | None, compact: bool = False) -> str:
    """Formata valor em Reais. Ex: 514000 → 'R$514.0k' (compact) ou 'R$514.000,00'."""
    if value is None:
        return "—"
    if compact:
        if abs(value) >= 1_000_000:
            return f"R${value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"R${value / 1_000:.1f}k"
    return f"R${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_usd(value: float | None, compact: bool = False) -> str:
    """Formata valor em Dólares. Ex: 13500 → 'US$13.5k' (compact) ou 'US$13,500.00'."""
    if value is None:
        return "—"
    if compact:
        if abs(value) >= 1_000_000:
            return f"US${value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"US${value / 1_000:.1f}k"
    return f"US${value:,.2f}"


def fmt_pct(value: float | None, decimals: int = 1, sign: bool = False) -> str:
    """Formata percentual. Ex: 14.3 → '+14.3%' (com sign) ou '14.3%'."""
    if value is None:
        return "—"
    prefix = "+" if sign and value > 0 else ""
    return f"{prefix}{value:.{decimals}f}%"


def fmt_number(value: float | None, decimals: int = 2) -> str:
    """Formata número genérico com separadores. Ex: 128450.5 → '128.450,50'."""
    if value is None:
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_date(value: str | date | datetime | None, short: bool = False) -> str:
    """Formata data. Ex: '2026-02-18' → '18/02/2026' ou '18/02' (short)."""
    if value is None:
        return "—"
    if isinstance(value, str):
        value = date.fromisoformat(value)
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d/%m") if short else value.strftime("%d/%m/%Y")


def fmt_delta(value: float | None) -> str:
    """Formata variação com seta. Ex: 1.5 → '↑ +1.5%', -0.3 → '↓ -0.3%'."""
    if value is None:
        return "—"
    if value > 0:
        return f"↑ +{value:.1f}%"
    if value < 0:
        return f"↓ {value:.1f}%"
    return "→ 0.0%"
