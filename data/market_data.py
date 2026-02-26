"""Cotações de mercado: BR (brapi) e US (yfinance), com cache Streamlit."""

import logging

import requests
import streamlit as st
import yfinance as yf

from utils.constants import CACHE_TTL_MACRO, CACHE_TTL_QUOTES, TICKERS_BR, TICKERS_NO_FUNDAMENTALS, TICKERS_US

logger = logging.getLogger(__name__)

BRAPI_BASE_URL = "https://brapi.dev/api"


# ============================================================
# Cotações BR — brapi.dev (fallback: yfinance .SA)
# ============================================================


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_quotes_br() -> dict[str, dict]:
    """Busca cotações BR via brapi. Retorna {ticker: {price, change_pct, ...}}."""
    try:
        return _fetch_brapi(TICKERS_BR)
    except Exception:
        logger.warning("brapi falhou, usando fallback yfinance .SA")
        return _fetch_yfinance_br(TICKERS_BR)


def _fetch_brapi(tickers: list[str]) -> dict[str, dict]:
    """Busca cotações via brapi.dev."""
    token = st.secrets.get("brapi", {}).get("token", "")
    joined = ",".join(tickers)
    url = f"{BRAPI_BASE_URL}/quote/{joined}"
    params = {"token": token} if token else {}

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = {}
    for item in data.get("results", []):
        ticker = item.get("symbol", "")
        results[ticker] = {
            "price": item.get("regularMarketPrice"),
            "change_pct": item.get("regularMarketChangePercent"),
            "change_abs": item.get("regularMarketChange"),
            "volume": item.get("regularMarketVolume"),
            "previous_close": item.get("regularMarketPreviousClose"),
            "market_cap": item.get("marketCap"),
            "currency": "BRL",
            "source": "brapi",
        }
    return results


def _fetch_yfinance_br(tickers: list[str]) -> dict[str, dict]:
    """Fallback: busca cotações BR via yfinance com sufixo .SA."""
    yf_tickers = [f"{t}.SA" for t in tickers]
    return _fetch_yfinance(yf_tickers, original_tickers=tickers, currency="BRL")


# ============================================================
# Cotações US — yfinance
# ============================================================


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_quotes_us() -> dict[str, dict]:
    """Busca cotações US via yfinance. Retorna {ticker: {price, change_pct, ...}}."""
    return _fetch_yfinance(TICKERS_US, currency="USD")


# ============================================================
# Helper yfinance
# ============================================================


def _fetch_yfinance(
    tickers: list[str],
    original_tickers: list[str] | None = None,
    currency: str = "USD",
) -> dict[str, dict]:
    """Busca cotações via yfinance para uma lista de tickers."""
    if not tickers:
        return {}

    results = {}
    data = yf.Tickers(" ".join(tickers))

    for i, yf_ticker in enumerate(tickers):
        original = original_tickers[i] if original_tickers else yf_ticker
        try:
            info = data.tickers[yf_ticker].fast_info
            results[original] = {
                "price": info.get("lastPrice"),
                "change_pct": _calc_change_pct(info.get("lastPrice"), info.get("previousClose")),
                "change_abs": _calc_change_abs(info.get("lastPrice"), info.get("previousClose")),
                "volume": info.get("lastVolume"),
                "previous_close": info.get("previousClose"),
                "market_cap": info.get("marketCap"),
                "currency": currency,
                "source": "yfinance",
            }
        except Exception:
            logger.warning(f"yfinance falhou para {yf_ticker}")
    return results


# ============================================================
# Todas as cotações (BR + US)
# ============================================================


def fetch_all_quotes() -> dict[str, dict]:
    """Busca cotações BR e US, retorna dict unificado {ticker: {price, ...}}."""
    quotes = {}
    quotes.update(fetch_quotes_br())
    quotes.update(fetch_quotes_us())
    return quotes


# ============================================================
# Variação semanal (5 dias úteis)
# ============================================================


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_weekly_changes() -> dict[str, float]:
    """Calcula variação % nos últimos 5 dias úteis para todos os tickers.

    Retorna {ticker: change_pct} com tickers originais (sem .SA).
    """
    all_yf = [f"{t}.SA" for t in TICKERS_BR] + list(TICKERS_US)
    rename_map = {f"{t}.SA": t for t in TICKERS_BR}
    rename_map.update({t: t for t in TICKERS_US})

    try:
        data = yf.download(all_yf, period="5d", progress=False)
        if data.empty:
            return {}

        import pandas as pd

        has_close = "Close" in data.columns or (
            hasattr(data.columns, "get_level_values") and "Close" in data.columns.get_level_values(0)
        )
        if not has_close:
            return {}

        closes = data["Close"]
        if isinstance(closes, pd.Series):
            closes = closes.to_frame(name=all_yf[0])

        results = {}
        for yf_ticker in all_yf:
            original = rename_map.get(yf_ticker, yf_ticker)
            if yf_ticker not in closes.columns:
                continue
            col = closes[yf_ticker].dropna()
            if len(col) < 2:
                continue
            first, last = col.iloc[0], col.iloc[-1]
            if first and first > 0:
                results[original] = round((last - first) / first * 100, 2)
        return results
    except Exception:
        logger.warning("fetch_weekly_changes: falhou")
        return {}


# ============================================================
# Histórico de preços (para gráficos e correlação)
# ============================================================


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_batch_price_history(
    tickers_br: list[str] | None = None,
    tickers_us: list[str] | None = None,
    period: str = "6mo",
):
    """Busca histórico de fechamento de múltiplos tickers em uma chamada.

    Retorna DataFrame com DatetimeIndex e uma coluna por ticker (nomes originais),
    ou None se não houver dados.
    """
    import pandas as pd

    all_yf = []
    rename_map = {}

    for t in tickers_br or []:
        yf_t = f"{t}.SA"
        all_yf.append(yf_t)
        rename_map[yf_t] = t
    for t in tickers_us or []:
        all_yf.append(t)
        rename_map[t] = t

    if not all_yf:
        return None

    try:
        data = yf.download(all_yf, period=period, progress=False)
    except Exception:
        logger.warning("fetch_batch_price_history: yf.download falhou")
        return None

    if data.empty:
        return None

    # Extrair coluna Close
    has_close = "Close" in data.columns
    if not has_close and hasattr(data.columns, "get_level_values"):
        has_close = "Close" in data.columns.get_level_values(0)

    if has_close:
        closes = data["Close"] if isinstance(data["Close"], pd.DataFrame) else data[["Close"]]
    else:
        return None

    # Renomear colunas de volta para tickers originais
    if isinstance(closes, pd.Series):
        ticker_name = all_yf[0]
        closes = closes.to_frame(name=rename_map.get(ticker_name, ticker_name))
    else:
        closes = closes.rename(columns=rename_map)

    # Remover colunas com todos NaN
    closes = closes.dropna(axis=1, how="all")
    return closes if not closes.empty else None


@st.cache_data(ttl=CACHE_TTL_QUOTES)
def fetch_price_history(ticker: str, period: str = "6mo", market: str = "BR"):
    """Retorna DataFrame com histórico de preços (Date, Close) via yfinance."""
    yf_ticker = f"{ticker}.SA" if market == "BR" else ticker
    data = yf.download(yf_ticker, period=period, progress=False)
    if data.empty:
        return None
    # yfinance retorna MultiIndex quando baixa 1 ticker via download; achatar
    if hasattr(data.columns, "droplevel"):
        data.columns = data.columns.droplevel(1) if data.columns.nlevels > 1 else data.columns
    return data[["Close"]].rename(columns={"Close": "close"}).reset_index()


# ============================================================
# Dados Fundamentalistas (yfinance .info)
# ============================================================

_YF_TO_FUNDAMENTAL = {
    "trailingPE": "trailing_pe",
    "forwardPE": "forward_pe",
    "priceToBook": "price_to_book",
    "enterpriseToEbitda": "ev_ebitda",
    "trailingAnnualDividendYield": "dividend_yield",
    "revenueGrowth": "revenue_growth",
    "profitMargins": "profit_margin",
    "returnOnEquity": "roe",
    "debtToEquity": "debt_to_equity",
}


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_fundamentals(tickers_br: list[str], tickers_us: list[str]) -> dict[str, dict]:
    """Busca dados fundamentalistas via yfinance .info.

    Returns:
        {ticker: {trailing_pe, forward_pe, price_to_book, ...}} com valores normalizados.
    """
    results = {}

    all_tickers = []
    for t in tickers_br:
        if t not in TICKERS_NO_FUNDAMENTALS:
            all_tickers.append((t, f"{t}.SA"))
    for t in tickers_us:
        if t not in TICKERS_NO_FUNDAMENTALS:
            all_tickers.append((t, t))

    for original, yf_symbol in all_tickers:
        try:
            ticker_obj = yf.Ticker(yf_symbol)
            info = ticker_obj.info
            if not info:
                continue

            fundamentals = {}
            for yf_key, our_key in _YF_TO_FUNDAMENTAL.items():
                fundamentals[our_key] = info.get(yf_key)

            results[original] = fundamentals
        except Exception:
            logger.warning("yfinance .info falhou para %s", yf_symbol)

    return results


# ============================================================
# Helpers
# ============================================================


def _calc_change_pct(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None or previous == 0:
        return None
    return ((current - previous) / previous) * 100


def _calc_change_abs(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None:
        return None
    return current - previous
