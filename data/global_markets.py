"""Dados de mercados globais: índices por região e commodities via yfinance."""

import logging

import streamlit as st
import yfinance as yf

from utils.constants import CACHE_TTL_QUOTES, COMMODITIES_TICKERS, GLOBAL_INDICES

logger = logging.getLogger(__name__)


# ============================================================
# Índices Globais
# ============================================================


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_global_indices() -> dict[str, list[dict]]:
    """Busca cotações de índices globais por região.

    Returns:
        {region: [{name, country, price, change_pct, ticker}, ...]}
    """
    results = {}
    for region, indices in GLOBAL_INDICES.items():
        region_data = []
        for idx in indices:
            try:
                info = yf.Ticker(idx["ticker"]).fast_info
                price = info.get("lastPrice")
                prev = info.get("previousClose")
                change_pct = None
                if price and prev and prev != 0:
                    change_pct = ((price - prev) / prev) * 100
                region_data.append(
                    {
                        "name": idx["name"],
                        "country": idx["country"],
                        "ticker": idx["ticker"],
                        "price": price,
                        "change_pct": change_pct,
                    }
                )
            except Exception:
                logger.warning("yfinance falhou para índice %s", idx["ticker"])
                region_data.append(
                    {
                        "name": idx["name"],
                        "country": idx["country"],
                        "ticker": idx["ticker"],
                        "price": None,
                        "change_pct": None,
                    }
                )
        results[region] = region_data
    return results


# ============================================================
# Commodities
# ============================================================


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_commodities() -> list[dict]:
    """Busca cotações de commodities via yfinance.

    Returns:
        [{name, ticker, unit, category, price, change_pct}, ...]
    """
    results = []
    for comm in COMMODITIES_TICKERS:
        try:
            info = yf.Ticker(comm["ticker"]).fast_info
            price = info.get("lastPrice")
            prev = info.get("previousClose")
            change_pct = None
            if price and prev and prev != 0:
                change_pct = ((price - prev) / prev) * 100
            results.append(
                {
                    "name": comm["name"],
                    "ticker": comm["ticker"],
                    "unit": comm["unit"],
                    "category": comm["category"],
                    "price": price,
                    "change_pct": change_pct,
                }
            )
        except Exception:
            logger.warning("yfinance falhou para commodity %s", comm["ticker"])
            results.append(
                {
                    "name": comm["name"],
                    "ticker": comm["ticker"],
                    "unit": comm["unit"],
                    "category": comm["category"],
                    "price": None,
                    "change_pct": None,
                }
            )
    return results
