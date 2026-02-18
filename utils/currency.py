"""Conversão de moedas BRL ↔ USD via PTAX do BCB."""

import logging

import requests
import streamlit as st

from utils.constants import BCB_SERIES, CACHE_TTL_MACRO

logger = logging.getLogger(__name__)

BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"


@st.cache_data(ttl=CACHE_TTL_MACRO)
def get_ptax() -> float:
    """Retorna câmbio PTAX venda (USD/BRL). Fallback: 5.75."""
    try:
        url = f"{BCB_BASE_URL}.{BCB_SERIES['ptax']}/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["valor"].replace(",", "."))
    except Exception:
        logger.warning("PTAX indisponível, usando fallback 5.75")
    return 5.75


def brl_to_usd(value_brl: float | None) -> float | None:
    """Converte BRL para USD usando PTAX."""
    if value_brl is None:
        return None
    ptax = get_ptax()
    return value_brl / ptax


def usd_to_brl(value_usd: float | None) -> float | None:
    """Converte USD para BRL usando PTAX."""
    if value_usd is None:
        return None
    ptax = get_ptax()
    return value_usd * ptax
