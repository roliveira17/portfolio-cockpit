"""Página Markets — Índices globais, commodities e curvas de juros."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.global_markets import fetch_commodities, fetch_global_indices
from data.yield_curve import fetch_br_yield_curve, fetch_us_treasury_curve
from utils.constants import REGION_LABELS
from utils.formatting import fmt_number, fmt_pct

st.header("🌍 Markets")

tab_indices, tab_commodities, tab_curves = st.tabs(["📈 Índices Globais", "🛢️ Commodities", "📐 Curva de Juros"])

# ============================================================
# Tab 1: Índices Globais
# ============================================================

with tab_indices:
    indices_data = fetch_global_indices()

    for region, label in REGION_LABELS.items():
        st.subheader(label)
        region_indices = indices_data.get(region, [])
        if not region_indices:
            st.info(f"Sem dados para {label}.")
            continue

        rows = []
        for idx in region_indices:
            price = idx.get("price")
            change = idx.get("change_pct")
            rows.append(
                {
                    "Índice": idx["name"],
                    "País": idx["country"],
                    "Cotação": fmt_number(price, decimals=0) if price else "—",
                    "Var. Dia": fmt_pct(change, sign=True) if change is not None else "—",
                    "_change": change or 0,
                }
            )

        df = pd.DataFrame(rows)
        st.dataframe(
            df[["Índice", "País", "Cotação", "Var. Dia"]].style.applymap(
                lambda v: "color: #2ca02c" if "+" in str(v) else "color: #d62728" if str(v).startswith("-") else "",
                subset=["Var. Dia"],
            ),
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# Tab 2: Commodities
# ============================================================

with tab_commodities:
    commodities = fetch_commodities()

    # KPI cards para principais commodities
    top_comms = commodities[:4] if len(commodities) >= 4 else commodities
    cols = st.columns(len(top_comms))
    for i, comm in enumerate(top_comms):
        with cols[i]:
            price = comm.get("price")
            change = comm.get("change_pct")
            price_str = f"{price:,.2f}" if price else "—"
            delta_str = fmt_pct(change, sign=True) if change is not None else None
            st.metric(comm["name"], price_str, delta_str)

    st.markdown("---")

    # Tabela completa
    st.subheader("Todas as Commodities")
    comm_rows = []
    for comm in commodities:
        price = comm.get("price")
        change = comm.get("change_pct")
        comm_rows.append(
            {
                "Commodity": comm["name"],
                "Cotação": f"{price:,.2f}" if price else "—",
                "Unidade": comm["unit"],
                "Var. Dia": fmt_pct(change, sign=True) if change is not None else "—",
                "Categoria": comm["category"].capitalize(),
            }
        )

    comm_df = pd.DataFrame(comm_rows)
    st.dataframe(
        comm_df.style.applymap(
            lambda v: "color: #2ca02c" if "+" in str(v) else "color: #d62728" if str(v).startswith("-") else "",
            subset=["Var. Dia"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    # BHKP manual input (migrado do Risk & Macro)
    st.markdown("---")
    st.subheader("Celulose BHKP (input manual)")
    bhkp_col1, bhkp_col2 = st.columns([2, 3])
    with bhkp_col1:
        bhkp_price = st.number_input(
            "Preço BHKP (USD/ton)",
            min_value=0.0,
            step=1.0,
            value=st.session_state.get("bhkp_price", 0.0),
            help="Inserir manualmente. Fonte: Fastmarkets ou relatórios setoriais.",
        )
        st.session_state["bhkp_price"] = bhkp_price
    with bhkp_col2:
        if bhkp_price > 0:
            st.metric("BHKP", f"US$ {bhkp_price:.0f}/ton")
        else:
            st.info("Insira o preço atual da celulose BHKP manualmente.")

# ============================================================
# Tab 3: Curva de Juros
# ============================================================

with tab_curves:
    col_br, col_us = st.columns(2)

    # --- Curva BR (DI x Pré) ---
    with col_br:
        st.subheader("🇧🇷 DI x Pré (B3)")
        br_curve = fetch_br_yield_curve()
        if br_curve is not None and not br_curve.empty:
            fig_br = go.Figure()
            fig_br.add_trace(
                go.Scatter(
                    x=br_curve["anos"],
                    y=br_curve["taxa"],
                    mode="lines+markers",
                    name="DI x Pré",
                    line=dict(color="#1f77b4", width=2),
                    marker=dict(size=4),
                )
            )
            fig_br.update_layout(
                xaxis_title="Anos",
                yaxis_title="Taxa (%)",
                height=350,
                margin=dict(t=20, b=40, l=50, r=20),
            )
            st.plotly_chart(fig_br, use_container_width=True)

            # Tabela resumida — vértices principais
            key_vertices = br_curve[br_curve["dias_corridos"].isin([21, 63, 126, 252, 504, 756, 1260, 2520])]
            if not key_vertices.empty:
                display = key_vertices[["dias_corridos", "anos", "taxa"]].copy()
                display.columns = ["Dias (DU)", "Anos", "Taxa (%)"]
                st.dataframe(display, use_container_width=True, hide_index=True)
        else:
            st.info("Curva DI x Pré indisponível. Verifique se é dia útil.")

    # --- Curva US (Treasury) ---
    with col_us:
        st.subheader("🇺🇸 Treasury Yields")
        us_curve = fetch_us_treasury_curve()
        if us_curve is not None and not us_curve.empty:
            ref_date = us_curve["date"].iloc[0] if "date" in us_curve.columns else ""

            fig_us = go.Figure()
            fig_us.add_trace(
                go.Scatter(
                    x=us_curve["years"],
                    y=us_curve["yield_pct"],
                    mode="lines+markers",
                    name="Treasury",
                    line=dict(color="#d62728", width=2),
                    marker=dict(size=4),
                    text=us_curve["label"],
                    hovertemplate="%{text}: %{y:.3f}%<extra></extra>",
                )
            )
            fig_us.update_layout(
                xaxis_title="Anos",
                yaxis_title="Yield (%)",
                height=350,
                margin=dict(t=20, b=40, l=50, r=20),
            )
            st.plotly_chart(fig_us, use_container_width=True)

            if ref_date:
                st.caption(f"Data de referência: {ref_date}")

            # Tabela
            display_us = us_curve[["label", "yield_pct"]].copy()
            display_us.columns = ["Vencimento", "Yield (%)"]
            st.dataframe(display_us, use_container_width=True, hide_index=True)
        else:
            st.info("Curva Treasury indisponível.")
