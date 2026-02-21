"""Curvas de juros: BR (DI x Pré via pyettj/B3) e US (Treasury via XML feed)."""

import logging
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from utils.constants import CACHE_TTL_MACRO, TREASURY_MATURITIES

logger = logging.getLogger(__name__)

TREASURY_XML_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"


# ============================================================
# BR — Curva DI x Pré (B3 via pyettj)
# ============================================================


@st.cache_data(ttl=CACHE_TTL_MACRO)
def fetch_br_yield_curve(ref_date: str | None = None) -> pd.DataFrame | None:
    """Busca curva DI x Pré da B3 via pyettj.

    Args:
        ref_date: Data de referência DD/MM/YYYY. Se None, usa hoje.

    Returns:
        DataFrame com colunas ['dias_corridos', 'taxa'] ou None se falhar.
    """
    try:
        import pyettj.ettj as ettj
    except ImportError:
        logger.warning("pyettj não instalado — curva BR indisponível")
        return None

    if ref_date is None:
        ref_date = datetime.now().strftime("%d/%m/%Y")

    try:
        df = ettj.get_ettj(ref_date, curva="PRE")
        if df is None or df.empty:
            return None

        # Normalizar nomes de colunas (pyettj pode variar)
        col_map = {}
        for col in df.columns:
            col_lower = col.lower().replace(" ", "_")
            if "dia" in col_lower and "corr" in col_lower:
                col_map[col] = "dias_corridos"
            elif "taxa" in col_lower:
                col_map[col] = "taxa"

        if col_map:
            df = df.rename(columns=col_map)

        # Garantir colunas essenciais
        if "dias_corridos" not in df.columns or "taxa" not in df.columns:
            logger.warning("pyettj retornou colunas inesperadas: %s", list(df.columns))
            return None

        df = df[["dias_corridos", "taxa"]].copy()
        df["dias_corridos"] = pd.to_numeric(df["dias_corridos"], errors="coerce")
        df["taxa"] = pd.to_numeric(df["taxa"], errors="coerce")
        df = df.dropna().sort_values("dias_corridos").reset_index(drop=True)

        # Converter dias corridos para anos (DU 252)
        df["anos"] = df["dias_corridos"] / 252

        return df
    except Exception:
        logger.warning("Falha ao buscar curva DI x Pré via pyettj")
        return None


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

        # Pegar a entrada mais recente (última)
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
