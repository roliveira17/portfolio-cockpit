"""Cálculos de portfólio: pesos, P&L, exposição setorial e por fator de risco."""

import pandas as pd

from utils.constants import FACTOR_SENSITIVITIES, SECTORS
from utils.currency import usd_to_brl


def build_portfolio_df(positions: list[dict], quotes: dict[str, dict]) -> pd.DataFrame:
    """Constrói DataFrame consolidado com posições + cotações + P&L.

    Args:
        positions: Lista de posições do DB (get_positions).
        quotes: Dict de cotações {ticker: {price, change_pct, ...}} (fetch_all_quotes).

    Returns:
        DataFrame com colunas: ticker, company_name, sector, market, currency,
        quantity, avg_price, total_invested, dividends_received, current_price,
        current_value_original, current_value_brl, pnl_abs, pnl_pct,
        pnl_with_div_pct, weight, target_weight, weight_gap, change_pct.
    """
    rows = []
    for pos in positions:
        ticker = pos["ticker"]
        quote = quotes.get(ticker, {})
        current_price = quote.get("price")
        change_pct = quote.get("change_pct")

        quantity = float(pos.get("quantity", 0))
        avg_price = float(pos.get("avg_price", 0))
        total_invested = float(pos.get("total_invested", 0))
        dividends = float(pos.get("dividends_received", 0))
        target_weight = float(pos.get("target_weight", 0))

        # Valor atual na moeda original
        current_value_original = quantity * current_price if current_price else None

        # Converter para BRL
        if pos["currency"] == "USD" and current_value_original is not None:
            current_value_brl = usd_to_brl(current_value_original)
        else:
            current_value_brl = current_value_original

        # P&L
        pnl_abs = (current_value_original - total_invested) if current_value_original else None
        pnl_pct = (pnl_abs / total_invested * 100) if pnl_abs is not None and total_invested > 0 else None
        pnl_with_div_pct = (
            ((pnl_abs + dividends) / total_invested * 100) if pnl_abs is not None and total_invested > 0 else None
        )

        rows.append(
            {
                "ticker": ticker,
                "company_name": pos.get("company_name", ""),
                "sector": pos.get("sector", ""),
                "market": pos.get("market", ""),
                "currency": pos.get("currency", ""),
                "analyst": pos.get("analyst", ""),
                "quantity": quantity,
                "avg_price": avg_price,
                "total_invested": total_invested,
                "dividends_received": dividends,
                "current_price": current_price,
                "current_value_original": current_value_original,
                "current_value_brl": current_value_brl,
                "pnl_abs": pnl_abs,
                "pnl_pct": pnl_pct,
                "pnl_with_div_pct": pnl_with_div_pct,
                "weight": 0.0,  # calculado abaixo
                "target_weight": target_weight,
                "weight_gap": 0.0,  # calculado abaixo
                "change_pct": change_pct,
            }
        )

    df = pd.DataFrame(rows)

    # Calcular pesos e gaps
    total_brl = df["current_value_brl"].sum()
    if total_brl and total_brl > 0:
        df["weight"] = (df["current_value_brl"] / total_brl * 100).round(2)
        df["weight_gap"] = (df["weight"] - df["target_weight"]).round(2)

    return df


def calc_total_patrimony(df: pd.DataFrame) -> float:
    """Retorna patrimônio total em BRL."""
    return df["current_value_brl"].sum() if not df.empty else 0.0


def calc_total_pnl(df: pd.DataFrame) -> tuple[float, float]:
    """Retorna (P&L absoluto em BRL, P&L %).

    Para posições US, converte o P&L de USD para BRL.
    """
    total_invested_brl = 0.0
    total_value_brl = 0.0

    for _, row in df.iterrows():
        invested = row["total_invested"]
        value = row["current_value_original"]
        if value is None:
            continue
        if row["currency"] == "USD":
            invested = usd_to_brl(invested)
            value = usd_to_brl(value)
        total_invested_brl += invested
        total_value_brl += value

    pnl_abs = total_value_brl - total_invested_brl
    pnl_pct = (pnl_abs / total_invested_brl * 100) if total_invested_brl > 0 else 0.0
    return pnl_abs, pnl_pct


def calc_sector_allocation(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna DataFrame com alocação setorial: sector, label, color, value_brl, weight."""
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby("sector")["current_value_brl"].sum().reset_index()
    grouped.columns = ["sector", "value_brl"]
    total = grouped["value_brl"].sum()
    grouped["weight"] = (grouped["value_brl"] / total * 100).round(2) if total > 0 else 0
    grouped["label"] = grouped["sector"].map(lambda s: SECTORS.get(s, {}).get("label", s))
    grouped["color"] = grouped["sector"].map(lambda s: SECTORS.get(s, {}).get("color", "#999"))
    return grouped.sort_values("weight", ascending=False).reset_index(drop=True)


def calc_factor_exposure(df: pd.DataFrame) -> dict[str, float]:
    """Calcula % do portfólio exposto a cada fator de risco.

    Retorna dict {fator: % exposição} baseado no mapeamento FACTOR_SENSITIVITIES.
    """
    if df.empty:
        return {}

    total = df["current_value_brl"].sum()
    if not total or total <= 0:
        return {}

    exposures = {}
    for factor, sensitivities in FACTOR_SENSITIVITIES.items():
        exposed_tickers = set(sensitivities.keys())
        exposed_value = df[df["ticker"].isin(exposed_tickers)]["current_value_brl"].sum()
        exposures[factor] = round(exposed_value / total * 100, 1)

    return exposures


def calc_top_movers(df: pd.DataFrame, n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (top_gainers, top_losers) DataFrames com n posições cada."""
    valid = df[df["change_pct"].notna()].copy()
    if valid.empty:
        empty = pd.DataFrame(columns=["ticker", "change_pct"])
        return empty, empty
    sorted_df = valid.sort_values("change_pct", ascending=False)
    gainers = sorted_df.head(n)[["ticker", "change_pct", "company_name"]].reset_index(drop=True)
    losers = (
        sorted_df.tail(n)[["ticker", "change_pct", "company_name"]].sort_values("change_pct").reset_index(drop=True)
    )
    return gainers, losers
