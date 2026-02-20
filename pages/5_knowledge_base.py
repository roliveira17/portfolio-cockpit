"""Página Knowledge Base — Repositório analítico por ação."""

import pandas as pd
import plotly.express as px
import streamlit as st

from data.db import (
    get_all_deep_dives,
    get_analysis_reports,
    get_deep_dives_by_ticker,
    get_next_deep_dive_version,
    insert_row,
)
from data.market_data import fetch_all_quotes
from utils.constants import (
    CONVICTION_LABELS,
    REPORT_TYPES,
    THESIS_STATUS,
    TICKERS_BR,
    TICKERS_US,
)

st.header("📚 Knowledge Base")

# ============================================================
# Busca full-text (2.17)
# ============================================================

search_query = st.text_input("🔍 Buscar", placeholder="Buscar por título, ticker, tags...")

tab_ticker, tab_reports, tab_timeline = st.tabs(["📄 Por Ticker", "📋 Relatórios", "📅 Timeline"])

# ============================================================
# Aba 1: Por Ticker (2.11)
# ============================================================

with tab_ticker:
    all_dives = get_all_deep_dives()

    # Tickers com deep dives
    tickers_with_dives = sorted(set(d["ticker"] for d in all_dives))
    if not tickers_with_dives:
        st.info("Nenhum deep dive encontrado.")
    else:
        selected_ticker = st.selectbox("Selecionar Ticker", tickers_with_dives)
        dives = get_deep_dives_by_ticker(selected_ticker)

        # Filtrar por busca
        if search_query:
            dives = [
                d for d in dives
                if search_query.lower() in (d.get("title") or "").lower()
                or search_query.lower() in (d.get("summary") or "").lower()
                or search_query.lower() in str(d.get("tags") or []).lower()
            ]

        st.markdown(f"**{selected_ticker}** — {len(dives)} versão(ões)")

        if dives:
            # Lista de versões
            for dive in dives:
                version = dive.get("version", 1)
                is_latest = version == dives[0]["version"]
                badge = " ← VIGENTE" if is_latest else ""
                status_emoji = ""
                if dive.get("thesis_status_at_time"):
                    s = THESIS_STATUS.get(dive["thesis_status_at_time"], {})
                    status_emoji = s.get("emoji", "")

                conv_label = CONVICTION_LABELS.get(dive.get("conviction_at_time", ""), "")
                target_str = f"Target: {dive['target_price_at_time']:.2f}" if dive.get("target_price_at_time") else ""

                label = f"v{version} ({dive.get('date', '?')}) {status_emoji} {conv_label} {target_str}{badge}"
                with st.expander(label):
                    if dive.get("summary"):
                        st.markdown(f"**Resumo:** {dive['summary']}")
                    if dive.get("key_changes"):
                        st.markdown(f"**Mudanças:** {dive['key_changes']}")
                    if dive.get("analyst"):
                        st.caption(f"Analista: {dive['analyst']}")

                    # Botões
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("📄 Ver completo", key=f"view_{dive['id']}"):
                            st.session_state[f"show_dive_{dive['id']}"] = True
                    with bc2:
                        content = dive.get("content_md", "")
                        st.download_button(
                            "📥 Download .md",
                            content,
                            f"{selected_ticker}_v{version}.md",
                            "text/markdown",
                            key=f"dl_{dive['id']}",
                        )

                    # Renderizar markdown se solicitado
                    if st.session_state.get(f"show_dive_{dive['id']}"):
                        st.markdown("---")
                        st.markdown(dive.get("content_md", ""), unsafe_allow_html=False)

            # --- Comparação entre versões (2.15) ---
            if len(dives) >= 2:
                st.markdown("---")
                st.subheader("Comparação entre Versões")
                cc1, cc2 = st.columns(2)
                version_labels = [f"v{d['version']} ({d.get('date', '?')})" for d in dives]
                with cc1:
                    v1_idx = st.selectbox("Versão A", range(len(dives)), format_func=lambda i: version_labels[i])
                with cc2:
                    v2_default = min(1, len(dives) - 1)
                    v2_idx = st.selectbox(
                        "Versão B", range(len(dives)),
                        index=v2_default, format_func=lambda i: version_labels[i],
                    )
                if v1_idx != v2_idx:
                    d1, d2 = dives[v1_idx], dives[v2_idx]
                    compare_fields = [
                        ("Status", "thesis_status_at_time"),
                        ("Convicção", "conviction_at_time"),
                        ("Target Price", "target_price_at_time"),
                    ]
                    compare_data = []
                    for label, field in compare_fields:
                        val_a = d1.get(field, "—") or "—"
                        val_b = d2.get(field, "—") or "—"
                        compare_data.append({
                            "Métrica": label,
                            version_labels[v1_idx]: val_a,
                            version_labels[v2_idx]: val_b,
                        })

                    # key_metrics comparison
                    km1 = d1.get("key_metrics") or {}
                    km2 = d2.get("key_metrics") or {}
                    all_keys = sorted(set(list(km1.keys()) + list(km2.keys())))
                    for k in all_keys:
                        compare_data.append({
                            "Métrica": k,
                            version_labels[v1_idx]: km1.get(k, "—"),
                            version_labels[v2_idx]: km2.get(k, "—"),
                        })

                    st.dataframe(pd.DataFrame(compare_data), use_container_width=True, hide_index=True)

            # --- Gráfico de evolução (2.16) ---
            if len(dives) >= 2:
                st.markdown("---")
                st.subheader("Evolução por Versão")
                evo_data = []
                for d in reversed(dives):  # cronológica
                    if d.get("date"):
                        row = {"Data": d["date"], "Versão": f"v{d['version']}"}
                        if d.get("target_price_at_time"):
                            row["Target Price"] = float(d["target_price_at_time"])
                        km = d.get("key_metrics") or {}
                        if "roic" in km:
                            row["ROIC (%)"] = float(km["roic"])
                        evo_data.append(row)
                if evo_data:
                    df_evo = pd.DataFrame(evo_data)
                    df_evo["Data"] = pd.to_datetime(df_evo["Data"])
                    numeric_cols = [c for c in df_evo.columns if c not in ("Data", "Versão")]
                    if numeric_cols:
                        fig_evo = px.line(df_evo, x="Data", y=numeric_cols, markers=True)
                        fig_evo.update_layout(height=300, margin=dict(t=30, b=30))
                        st.plotly_chart(fig_evo, use_container_width=True)

    # --- Upload de novo deep dive (2.14) ---
    st.markdown("---")
    st.subheader("Upload Novo Deep Dive")
    with st.expander("➕ Adicionar Deep Dive"):
        with st.form("upload_deep_dive"):
            all_tickers = sorted(TICKERS_BR + TICKERS_US)
            upload_ticker = st.selectbox("Ticker", all_tickers, key="upload_ticker")
            upload_content = st.text_area("Conteúdo Markdown", height=200)

            uc1, uc2 = st.columns(2)
            with uc1:
                upload_title = st.text_input("Título")
                upload_status = st.selectbox(
                    "Status da tese", list(THESIS_STATUS.keys()),
                    format_func=lambda x: f"{THESIS_STATUS[x]['emoji']} {THESIS_STATUS[x]['label']}",
                    key="upload_status",
                )
            with uc2:
                upload_conviction = st.selectbox(
                    "Convicção", list(CONVICTION_LABELS.keys()),
                    format_func=lambda x: CONVICTION_LABELS[x],
                    key="upload_conv",
                )
                upload_target = st.number_input("Target Price", min_value=0.0, step=0.01, key="upload_target")

            upload_changes = st.text_area("Mudanças vs. versão anterior", height=60)

            if st.form_submit_button("📤 Upload"):
                if upload_content and upload_title:
                    next_ver = get_next_deep_dive_version(upload_ticker)
                    quotes = fetch_all_quotes()
                    current = quotes.get(upload_ticker, {}).get("price")
                    insert_row("deep_dives", {
                        "ticker": upload_ticker,
                        "version": next_ver,
                        "title": upload_title,
                        "content_md": upload_content,
                        "summary": upload_content[:500] if len(upload_content) > 500 else upload_content,
                        "thesis_status_at_time": upload_status,
                        "conviction_at_time": upload_conviction,
                        "target_price_at_time": upload_target or None,
                        "current_price_at_time": current,
                        "key_changes": upload_changes,
                        "key_metrics": {},
                        "tags": ["manual_upload"],
                        "date": str(pd.Timestamp.now().date()),
                    })
                    st.success(f"Deep dive v{next_ver} de {upload_ticker} criado!")
                    st.rerun()
                else:
                    st.error("Título e conteúdo são obrigatórios.")

# ============================================================
# Aba 2: Relatórios (2.12)
# ============================================================

with tab_reports:
    reports = get_analysis_reports()

    # Filtros
    rc1, rc2 = st.columns(2)
    with rc1:
        type_filter = st.selectbox(
            "Tipo", ["Todos"] + list(REPORT_TYPES.keys()),
            format_func=lambda x: "Todos" if x == "Todos" else REPORT_TYPES[x],
        )
    with rc2:
        all_tags = set()
        for r in reports:
            all_tags.update(r.get("tags") or [])
        tag_filter = st.multiselect("Tags", sorted(all_tags))

    # Filtrar
    filtered = reports
    if type_filter != "Todos":
        filtered = [r for r in filtered if r.get("report_type") == type_filter]
    if tag_filter:
        filtered = [r for r in filtered if set(tag_filter) & set(r.get("tags") or [])]
    if search_query:
        filtered = [
            r for r in filtered
            if search_query.lower() in (r.get("title") or "").lower()
            or search_query.lower() in (r.get("summary") or "").lower()
            or search_query.lower() in str(r.get("tags") or []).lower()
        ]

    if not filtered:
        st.info("Nenhum relatório encontrado.")
    else:
        for report in filtered:
            type_label = REPORT_TYPES.get(report.get("report_type", ""), "—")
            tags_str = ", ".join(report.get("tags") or [])
            tickers_str = ", ".join(report.get("tickers_mentioned") or [])

            with st.expander(f"📄 {report['title']} — {report.get('date', '?')} ({type_label})"):
                if tags_str:
                    st.caption(f"Tags: {tags_str}")
                if tickers_str:
                    st.caption(f"Tickers: {tickers_str}")
                if report.get("summary"):
                    st.markdown(f"**Resumo:** {report['summary']}")

                rbc1, rbc2 = st.columns(2)
                with rbc1:
                    if st.button("📄 Ver completo", key=f"view_report_{report['id']}"):
                        st.session_state[f"show_report_{report['id']}"] = True
                with rbc2:
                    st.download_button(
                        "📥 Download .md",
                        report.get("content_md", ""),
                        f"{report['title'].replace(' ', '_')}.md",
                        "text/markdown",
                        key=f"dl_report_{report['id']}",
                    )

                if st.session_state.get(f"show_report_{report['id']}"):
                    st.markdown("---")
                    st.markdown(report.get("content_md", ""), unsafe_allow_html=False)

# ============================================================
# Aba 3: Timeline (2.13)
# ============================================================

with tab_timeline:
    all_dives = get_all_deep_dives()
    all_reports = get_analysis_reports()

    timeline_items = []
    for d in all_dives:
        if d.get("date"):
            timeline_items.append({
                "Data": d["date"],
                "Título": d.get("title", d["ticker"]),
                "Tipo": "Deep Dive",
                "Ticker": d["ticker"],
                "Versão": f"v{d.get('version', 1)}",
            })
    for r in all_reports:
        if r.get("date"):
            timeline_items.append({
                "Data": r["date"],
                "Título": r.get("title", "—"),
                "Tipo": "Relatório",
                "Ticker": ", ".join(r.get("tickers_mentioned") or ["—"]),
                "Versão": "",
            })

    if search_query:
        timeline_items = [
            t for t in timeline_items
            if search_query.lower() in t["Título"].lower()
            or search_query.lower() in t["Ticker"].lower()
        ]

    if timeline_items:
        df_tl = pd.DataFrame(timeline_items)
        df_tl["Data"] = pd.to_datetime(df_tl["Data"])
        df_tl = df_tl.sort_values("Data")

        color_map = {"Deep Dive": "#1f77b4", "Relatório": "#ff7f0e"}
        fig_tl = px.scatter(
            df_tl, x="Data", y="Ticker", color="Tipo",
            color_discrete_map=color_map,
            hover_data=["Título", "Versão"],
            size_max=12,
        )
        fig_tl.update_traces(marker=dict(size=12))
        fig_tl.update_layout(
            height=max(300, len(df_tl["Ticker"].unique()) * 40 + 100),
            margin=dict(t=30, b=30),
            xaxis_title="",
            yaxis_title="",
        )
        st.plotly_chart(fig_tl, use_container_width=True)

        st.dataframe(
            df_tl[["Data", "Tipo", "Ticker", "Título", "Versão"]].sort_values("Data", ascending=False),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("Nenhum documento encontrado.")
