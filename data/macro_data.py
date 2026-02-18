"""Indicadores macroeconômicos: BCB (Brasil) + yfinance (Global), com cache."""

import logging

import requests
import streamlit as st
import yfinance as yf

from utils.constants import BCB_SERIES, CACHE_TTL_MACRO, MACRO_TICKERS

logger = logging.getLogger(__name__)

BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"


# ============================================================
# BCB — Indicadores Brasil
# ============================================================


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_bcb_indicator(series_id: int) -> float | None:
    """Busca último valor de uma série BCB SGS."""
    try:
        url = f"{BCB_BASE_URL}.{series_id}/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["valor"].replace(",", "."))
    except Exception:
        logger.warning(f"BCB série {series_id} falhou")
    return None


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_macro_br() -> dict[str, float | None]:
    """Busca indicadores macro Brasil (Selic, IPCA, CDI, PTAX)."""
    return {
        "selic": fetch_bcb_indicator(BCB_SERIES["selic"]),
        "ipca_12m": fetch_bcb_indicator(BCB_SERIES["ipca_12m"]),
        "cdi": fetch_bcb_indicator(BCB_SERIES["cdi"]),
        "usd_brl": fetch_bcb_indicator(BCB_SERIES["ptax"]),
    }


# ============================================================
# yfinance — Indicadores Globais
# ============================================================


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_macro_global() -> dict[str, dict | None]:
    """Busca indicadores globais via yfinance. Retorna {nome: {value, change_pct}}."""
    results = {}
    for name, ticker in MACRO_TICKERS.items():
        try:
            info = yf.Ticker(ticker).fast_info
            price = info.get("lastPrice")
            prev = info.get("previousClose")
            change_pct = None
            if price and prev and prev != 0:
                change_pct = ((price - prev) / prev) * 100
            results[name] = {"value": price, "change_pct": change_pct}
        except Exception:
            logger.warning(f"yfinance falhou para {ticker} ({name})")
            results[name] = None
    return results


# ============================================================
# Snapshot consolidado
# ============================================================


def fetch_macro_snapshot() -> dict[str, float | None]:
    """Retorna snapshot consolidado de todos os indicadores macro."""
    br = fetch_macro_br()
    gl = fetch_macro_global()

    return {
        "selic": br.get("selic"),
        "ipca_12m": br.get("ipca_12m"),
        "usd_brl": br.get("usd_brl"),
        "dxy": _extract_value(gl.get("dxy")),
        "ibov": _extract_value(gl.get("ibov")),
        "sp500": _extract_value(gl.get("sp500")),
        "vix": _extract_value(gl.get("vix")),
        "brent": _extract_value(gl.get("brent")),
        "treasury_10y": _extract_value(gl.get("treasury_10y")),
    }


def _extract_value(data: dict | None) -> float | None:
    if data is None:
        return None
    return data.get("value")
