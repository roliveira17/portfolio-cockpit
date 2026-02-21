"""Indicador de freshness dos dados — tracking de última atualização."""

from datetime import datetime

import streamlit as st


def record_fetch_time(key: str) -> None:
    """Registra o horário de uma atualização de dados no session_state."""
    if "_cache_timestamps" not in st.session_state:
        st.session_state["_cache_timestamps"] = {}
    st.session_state["_cache_timestamps"][key] = datetime.now()


def get_fetch_time(key: str) -> datetime | None:
    """Retorna o horário da última atualização para uma chave."""
    timestamps = st.session_state.get("_cache_timestamps", {})
    return timestamps.get(key)


def show_freshness_badge(key: str, label: str = "Dados") -> None:
    """Exibe badge de freshness no canto da página.

    Mostra "Dados atualizados há X min" ou "Dados não carregados".
    """
    ts = get_fetch_time(key)
    if ts is None:
        st.caption(f"⏳ {label}: carregando...")
        return

    delta = datetime.now() - ts
    minutes = int(delta.total_seconds() / 60)

    if minutes < 1:
        text = f"🟢 {label} atualizados agora"
    elif minutes < 15:
        text = f"🟢 {label} atualizados há {minutes} min"
    elif minutes < 60:
        text = f"🟡 {label} atualizados há {minutes} min"
    else:
        hours = minutes // 60
        text = f"🟠 {label} atualizados há {hours}h{minutes % 60:02d}"

    st.caption(text)
