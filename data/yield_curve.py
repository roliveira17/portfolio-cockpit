"""Curvas de juros: BR (DI x Pre via pyettj/B3) e US (Treasury via XML feed)."""

import logging
from datetime import date, datetime, timedelta

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from utils.constants import CACHE_TTL_MACRO, TREASURY_MATURITIES

logger = logging.getLogger(__name__)

TREASURY_XML_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"

MAX_BUSINESS_DAY_RETRIES = 5


# ============================================================
# BR — Curva DI x Pre (B3 via pyettj)
# ============================================================


def _get_last_business_day(ref_date: date) -> date:
    """Retorna ref_date se dia util, senao a sexta anterior."""
    weekday = ref_date.weekday()
    if weekday == 5:  # sabado
        return ref_date - timedelta(days=1)
    if weekday == 6:  # domingo
        return ref_date - timedelta(days=2)
    return ref_date


def _fetch_ettj(date_str: str) -> pd.DataFrame | None:
    """Chama pyettj.get_ettj e retorna DataFrame cru ou None."""
    try:
        import pyettj.ettj as ettj
    except ImportError:
        logger.warning("pyettj nao instalado — curva BR indisponivel")
        return None

    try:
        df = ettj.get_ettj(date_str, curva="PRE")
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        logger.warning("pyettj falhou para %s: %s", date_str, e)
        return None


def _normalize_ettj_df(df: pd.DataFrame) -> pd.DataFrame | None:
    """Normaliza colunas do DataFrame retornado pelo pyettj."""
    col_map = {}
    for col in df.columns:
        col_lower = col.lower().replace(" ", "_")
        if "dia" in col_lower and "corr" in col_lower:
            col_map[col] = "dias_corridos"
        elif "taxa" in col_lower:
            col_map[col] = "taxa"

    if col_map:
        df = df.rename(columns=col_map)

    if "dias_corridos" not in df.columns or "taxa" not in df.columns:
        logger.warning("pyettj retornou colunas inesperadas: %s", list(df.columns))
        return None

    df = df[["dias_corridos", "taxa"]].copy()
    df["dias_corridos"] = pd.to_numeric(df["dias_corridos"], errors="coerce")
    df["taxa"] = pd.to_numeric(df["taxa"], errors="coerce")
    df = df.dropna().sort_values("dias_corridos").reset_index(drop=True)
    df["anos"] = df["dias_corridos"] / 252

    return df


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_br_yield_curve(ref_date: str | None = None) -> tuple[pd.DataFrame | None, date | None]:
    """Busca curva DI x Pre da B3 via pyettj.

    Args:
        ref_date: Data de referencia DD/MM/YYYY. Se None, usa hoje.

    Returns:
        Tupla (DataFrame com colunas ['dias_corridos', 'taxa', 'anos'], data_efetiva)
        ou (None, None) se falhar.
    """
    if ref_date is not None:
        try:
            target = datetime.strptime(ref_date, "%d/%m/%Y").date()
        except ValueError:
            logger.warning("Data invalida: %s", ref_date)
            return None, None
    else:
        target = date.today()

    target = _get_last_business_day(target)

    for attempt in range(MAX_BUSINESS_DAY_RETRIES):
        candidate = target - timedelta(days=attempt)
        candidate = _get_last_business_day(candidate)
        date_str = candidate.strftime("%d/%m/%Y")

        raw_df = _fetch_ettj(date_str)
        if raw_df is not None:
            normalized = _normalize_ettj_df(raw_df)
            if normalized is not None and not normalized.empty:
                logger.info("Curva DI obtida para %s", date_str)
                return normalized, candidate

        logger.debug("Sem dados para %s, tentando dia anterior", date_str)

    logger.warning("Curva DI indisponivel apos %d tentativas", MAX_BUSINESS_DAY_RETRIES)
    return None, None


# ============================================================
# US — Treasury Yield Curve (XML feed)
# ============================================================


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_us_treasury_curve(year: int | None = None) -> pd.DataFrame | None:
    """Busca curva de juros US Treasury via XML feed do Treasury.gov.

    Returns:
        DataFrame com a curva mais recente: colunas ['label', 'years', 'yield_pct']
        ou None se falhar.
    """
    if year is None:
        year = datetime.now().year

    try:
        params = {
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value": str(year),
        }
        resp = requests.get(TREASURY_XML_URL, params=params, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "xml")
        entries = soup.find_all("entry")
        if not entries:
            return None

        # Pegar a entrada mais recente (ultima)
        latest = entries[-1]

        date_elem = latest.find("d:NEW_DATE")
        ref_date = date_elem.text[:10] if date_elem and date_elem.text else None

        rows = []
        for mat in TREASURY_MATURITIES:
            elem = latest.find(mat["tag"])
            yield_val = float(elem.text) if elem and elem.text else None
            rows.append(
                {
                    "label": mat["label"],
                    "years": mat["years"],
                    "yield_pct": yield_val,
                    "date": ref_date,
                }
            )

        df = pd.DataFrame(rows).dropna(subset=["yield_pct"])
        return df if not df.empty else None

    except Exception:
        logger.warning("Falha ao buscar Treasury yield curve")
        return None
