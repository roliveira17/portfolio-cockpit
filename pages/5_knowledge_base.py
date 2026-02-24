"""Pagina Knowledge Base — Card-based layout unificando deep dives e relatorios."""

import pandas as pd
import streamlit as st

from data.db import get_all_deep_dives, get_analysis_reports, get_deep_dives_by_ticker
from utils.auth import check_auth
from utils.constants import (
    CONVICTION_LABELS,
    REPORT_TYPES,
    SECTORS,
    THESIS_STATUS,
    TICKER_SECTOR,
)

check_auth()


def _fix_encoding(text: str) -> str:
    """Try latin-1 -> utf-8 re-encode; fall back to original."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


def _build_unified_items() -> list[dict]:
    """Merge deep_dives and analysis_reports into a single list of cards."""
    items: list[dict] = []

    for d in get_all_deep_dives():
        sector_key = TICKER_SECTOR.get(d.get("ticker", ""), "")
        sector_label = SECTORS.get(sector_key, {}).get("label", "")
        items.append(
            {
                "source": "deep_dive",
                "id": d["id"],
                "ticker": d.get("ticker", ""),
                "title": d.get("title", d.get("ticker", "—")),
                "date": d.get("date", ""),
                "summary": d.get("summary", ""),
                "content_md": d.get("content_md", ""),
                "version": d.get("version", 1),
                "status": d.get("thesis_status_at_time", ""),
                "conviction": d.get("conviction_at_time", ""),
                "sector_key": sector_key,
                "sector_label": sector_label,
                "tags": d.get("tags") or [],
                "key_metrics": d.get("key_metrics") or {},
                "type_label": "Deep Dive",
            }
        )

    for r in get_analysis_reports():
        items.append(
            {
                "source": "report",
                "id": r["id"],
                "ticker": ", ".join(r.get("tickers_mentioned") or []),
                "title": r.get("title", "—"),
                "date": r.get("date", ""),
                "summary": r.get("summary", ""),
                "content_md": r.get("content_md", ""),
                "version": None,
                "status": "",
                "conviction": "",
                "sector_key": "",
                "sector_label": "",
                "tags": r.get("tags") or [],
                "key_metrics": {},
                "type_label": REPORT_TYPES.get(r.get("report_type", ""), "Relatorio"),
            }
        )

    items.sort(key=lambda x: x.get("date") or "", reverse=True)
    return items


def _apply_filters(
    items: list[dict],
    search: str,
    tickers: list[str],
    doc_type: str,
    status: str,
    conviction: str,
    sectors: list[str],
    date_start,
    date_end,
) -> list[dict]:
    """Apply all client-side filters to the unified items list."""
    filtered = items

    if search:
        q = search.lower()
        filtered = [
            i
            for i in filtered
            if q in (i["title"] or "").lower()
            or q in (i["summary"] or "").lower()
            or q in (i["content_md"] or "").lower()
            or q in (i["ticker"] or "").lower()
            or q in " ".join(i["tags"]).lower()
        ]

    if tickers:
        filtered = [i for i in filtered if i["ticker"] in tickers or any(t in i["ticker"] for t in tickers)]

    if doc_type == "Deep Dive":
        filtered = [i for i in filtered if i["source"] == "deep_dive"]
    elif doc_type == "Relatorio":
        filtered = [i for i in filtered if i["source"] == "report"]

    if status != "Todos":
        filtered = [i for i in filtered if i["status"] == status]

    if conviction != "Todos":
        filtered = [i for i in filtered if i["conviction"] == conviction]

    if sectors:
        filtered = [i for i in filtered if i["sector_key"] in sectors]

    if date_start:
        ds = str(date_start)
        filtered = [i for i in filtered if (i["date"] or "") >= ds]
    if date_end:
        de = str(date_end)
        filtered = [i for i in filtered if (i["date"] or "") <= de]

    return filtered


def _render_card(item: dict, ticker_version_counts: dict[str, int]) -> None:
    """Render a single card inside a bordered container."""
    ticker = item["ticker"]
    status_info = THESIS_STATUS.get(item["status"], {})
    status_str = f"{status_info.get('emoji', '')} {status_info.get('label', '')}" if status_info else ""
    conv_str = CONVICTION_LABELS.get(item["conviction"], "")
    sector_str = item["sector_label"]
    version_str = f"v{item['version']}" if item["version"] else ""

    # Header line
    icon = "📄" if item["source"] == "deep_dive" else "📋"
    header = f"**{icon} {item['type_label']}  {ticker} — {item['title']}    {item['date'] or ''}**"

    # Metadata line
    meta_parts = [p for p in [status_str, f"Conv: {conv_str}" if conv_str else "", sector_str, version_str] if p]
    meta_line = " | ".join(meta_parts)

    summary_text = (item["summary"] or "")[:200]
    if len(item.get("summary") or "") > 200:
        summary_text += "..."

    with st.container(border=True):
        st.markdown(header)
        if meta_line:
            st.caption(meta_line)
        if summary_text:
            st.markdown(f"Resumo: {summary_text}")

        col_dl, col_cmp = st.columns([2, 3])
        with col_dl:
            filename = f"{ticker.replace(', ', '_')}_{version_str or 'report'}.md"
            st.download_button(
                "📥 Download",
                item["content_md"] or "",
                filename,
                "text/markdown",
                key=f"dl_{item['id']}",
            )
        with col_cmp:
            has_versions = item["source"] == "deep_dive" and ticker_version_counts.get(ticker, 0) > 1
            if has_versions:
                if st.button("🔄 Comparar versoes", key=f"cmp_{item['id']}"):
                    st.session_state["compare_ticker"] = ticker

        with st.expander("▶ Ver completo"):
            content = _fix_encoding(item["content_md"] or "")
            st.markdown(content, unsafe_allow_html=False)


def _render_comparison(ticker: str) -> None:
    """Render side-by-side version comparison for a ticker."""
    st.subheader(f"Comparacao de Versoes — {ticker}")
    dives = get_deep_dives_by_ticker(ticker)
    if len(dives) < 2:
        st.info("Menos de 2 versoes disponiveis.")
        return

    version_labels = [f"v{d['version']} ({d.get('date', '?')})" for d in dives]
    c1, c2, c3 = st.columns([3, 3, 2])
    with c1:
        v1_idx = st.selectbox("Versao A", range(len(dives)), format_func=lambda i: version_labels[i])
    with c2:
        v2_idx = st.selectbox(
            "Versao B", range(len(dives)), index=min(1, len(dives) - 1), format_func=lambda i: version_labels[i]
        )
    with c3:
        if st.button("Fechar comparacao"):
            del st.session_state["compare_ticker"]
            st.rerun()

    if v1_idx == v2_idx:
        st.warning("Selecione versoes diferentes.")
        return

    d1, d2 = dives[v1_idx], dives[v2_idx]
    rows: list[dict] = []
    for label, field in [
        ("Status", "thesis_status_at_time"),
        ("Conviccao", "conviction_at_time"),
        ("Target Price", "target_price_at_time"),
    ]:
        rows.append(
            {
                "Metrica": label,
                version_labels[v1_idx]: d1.get(field, "—") or "—",
                version_labels[v2_idx]: d2.get(field, "—") or "—",
            }
        )

    km1, km2 = d1.get("key_metrics") or {}, d2.get("key_metrics") or {}
    for k in sorted(set(list(km1.keys()) + list(km2.keys()))):
        rows.append({"Metrica": k, version_labels[v1_idx]: km1.get(k, "—"), version_labels[v2_idx]: km2.get(k, "—")})

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ========================== Page layout ==========================

st.header("📚 Knowledge Base")
search_query = st.text_input("🔍 Buscar", placeholder="Buscar por titulo, ticker, tags, conteudo...")

all_items = _build_unified_items()
all_tickers_in_data = sorted(set(i["ticker"] for i in all_items if i["source"] == "deep_dive"))

r2c1, r2c2, r2c3, r2c4 = st.columns([3, 2, 2, 2])
with r2c1:
    sel_tickers = st.multiselect("Ticker", all_tickers_in_data)
with r2c2:
    sel_type = st.selectbox("Tipo", ["Todos", "Deep Dive", "Relatorio"])
with r2c3:
    status_opts = ["Todos"] + list(THESIS_STATUS.keys())
    sel_status = st.selectbox(
        "Status",
        status_opts,
        format_func=lambda x: "Todos" if x == "Todos" else f"{THESIS_STATUS[x]['emoji']} {THESIS_STATUS[x]['label']}",
    )
with r2c4:
    conv_opts = ["Todos"] + list(CONVICTION_LABELS.keys())
    sel_conviction = st.selectbox(
        "Conviccao",
        conv_opts,
        format_func=lambda x: "Todos" if x == "Todos" else CONVICTION_LABELS[x],
    )

# Row 3: Sector, Date range
r3c1, r3c2, r3c3 = st.columns([4, 3, 3])
with r3c1:
    sector_opts = [k for k in SECTORS if k not in ("fundos", "caixa")]
    sel_sectors = st.multiselect(
        "Setor",
        sector_opts,
        format_func=lambda x: SECTORS[x]["label"],
    )
with r3c2:
    sel_date_start = st.date_input("De", value=None, key="kb_date_start")
with r3c3:
    sel_date_end = st.date_input("Ate", value=None, key="kb_date_end")

st.divider()

# Version comparison panel (if active)
if "compare_ticker" in st.session_state:
    _render_comparison(st.session_state["compare_ticker"])
    st.divider()

# Apply filters and render cards
filtered = _apply_filters(
    all_items,
    search_query,
    sel_tickers,
    sel_type,
    sel_status,
    sel_conviction,
    sel_sectors,
    sel_date_start,
    sel_date_end,
)

# Pre-compute version counts per ticker for "Comparar versoes" button visibility
ticker_version_counts: dict[str, int] = {}
for item in all_items:
    if item["source"] == "deep_dive":
        t = item["ticker"]
        ticker_version_counts[t] = ticker_version_counts.get(t, 0) + 1

if not filtered:
    st.info("Nenhum documento encontrado com os filtros atuais.")
else:
    st.caption(f"{len(filtered)} documento(s) encontrado(s)")
    for item in filtered:
        _render_card(item, ticker_version_counts)
