"""Página Thesis Board — Gestão de teses de investimento."""

from datetime import date, timedelta

import plotly.express as px
import streamlit as st

from data.db import (
    delete_row,
    get_all_catalysts,
    get_catalysts_by_ticker,
    get_positions,
    get_theses,
    get_thesis_by_ticker,
    insert_row,
    update_row,
)
from data.market_data import fetch_all_quotes
from utils.constants import (
    CATALYST_CATEGORIES,
    CONVICTION_LABELS,
    IMPACT_LABELS,
    MOAT_LABELS,
    MOAT_TREND_LABELS,
    THESIS_STATUS,
)
from utils.formatting import fmt_pct

# ============================================================
# Helpers
# ============================================================


def _calc_target_price(bull: float, base: float, bear: float) -> float | None:
    """Target ponderado 20/60/20."""
    if bull and base and bear:
        return bull * 0.20 + base * 0.60 + bear * 0.20
    return None


def _calc_margin_of_safety(target: float | None, current: float | None) -> float | None:
    """Margem de segurança = (Target - Atual) / Target."""
    if target and current and target > 0:
        return (target - current) / target * 100
    return None


# ============================================================
# Layout
# ============================================================

st.header("📋 Thesis Board")

positions = get_positions(active_only=True)
theses = get_theses()
quotes = fetch_all_quotes()
thesis_map = {t["ticker"]: t for t in theses}

# Tickers de ações (excluindo fundos e caixa)
stock_tickers = [p["ticker"] for p in positions if p["sector"] not in ("fundos", "caixa")]

# --- Alertas de revisão vencida (2.7) ---
overdue = [
    t for t in theses
    if t.get("next_review") and t["next_review"] < str(date.today())
]
if overdue:
    tickers_str = ", ".join(t["ticker"] for t in overdue)
    st.warning(f"⚠️ Revisão vencida: {tickers_str}")

# ============================================================
# Kanban (2.1)
# ============================================================

st.subheader("Visão por Status")

col_green, col_yellow, col_red = st.columns(3)

for col, status_key in [(col_green, "GREEN"), (col_yellow, "YELLOW"), (col_red, "RED")]:
    info = THESIS_STATUS[status_key]
    with col:
        st.markdown(f"### {info['emoji']} {info['label']}")
        status_theses = [t for t in theses if t.get("status") == status_key]
        if not status_theses:
            st.caption("Nenhuma tese")
        for t in status_theses:
            ticker = t["ticker"]
            conviction = CONVICTION_LABELS.get(t.get("conviction", ""), "—")
            moat = MOAT_LABELS.get(t.get("moat_rating", ""), "—")
            # Calcular upside
            quote = quotes.get(ticker, {})
            current_price = quote.get("price")
            target = t.get("target_price")
            upside = ""
            if target and current_price and current_price > 0:
                upside_val = (target / current_price - 1) * 100
                upside = f" | Upside: {upside_val:+.0f}%"
            # Badge de revisão vencida
            overdue_badge = ""
            if t.get("next_review") and t["next_review"] < str(date.today()):
                overdue_badge = " 🔴"
            st.markdown(
                f"**{ticker}**{overdue_badge}  \n"
                f"Convicção: {conviction} | Moat: {moat}{upside}"
            )

# Teses sem registro
tickers_with_thesis = {t["ticker"] for t in theses}
tickers_without = [t for t in stock_tickers if t not in tickers_with_thesis]
if tickers_without:
    st.caption(f"Sem tese: {', '.join(tickers_without)}")

# ============================================================
# Detalhes e CRUD (2.2, 2.6)
# ============================================================

st.markdown("---")
st.subheader("Detalhes da Tese")

selected_ticker = st.selectbox("Selecionar posição", stock_tickers)
thesis = get_thesis_by_ticker(selected_ticker)
position = next((p for p in positions if p["ticker"] == selected_ticker), None)
quote = quotes.get(selected_ticker, {})
current_price = quote.get("price", 0)

# --- Métricas calculadas ---
if thesis:
    target = _calc_target_price(
        thesis.get("bull_case_price") or 0,
        thesis.get("base_case_price") or 0,
        thesis.get("bear_case_price") or 0,
    )
    margin = _calc_margin_of_safety(target, current_price)
    upside = ((target / current_price) - 1) * 100 if target and current_price else None

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Preço Atual", f"{current_price:.2f}" if current_price else "—")
    mc2.metric("Target (20/60/20)", f"{target:.2f}" if target else "—")
    mc3.metric("Upside", fmt_pct(upside, sign=True) if upside is not None else "—")
    mc4.metric("Margem Segurança", fmt_pct(margin, sign=True) if margin is not None else "—")

# --- Formulário de edição ---
with st.form(f"thesis_form_{selected_ticker}"):
    st.markdown(f"**{selected_ticker}** — {position['company_name'] if position else ''}")

    fc1, fc2 = st.columns(2)
    with fc1:
        status_options = list(THESIS_STATUS.keys())
        current_status = thesis.get("status", "GREEN") if thesis else "GREEN"
        status_idx = status_options.index(current_status) if current_status in status_options else 0
        status = st.selectbox(
            "Status", status_options,
            index=status_idx,
            format_func=lambda x: f"{THESIS_STATUS[x]['emoji']} {THESIS_STATUS[x]['label']}",
        )

        conviction_options = list(CONVICTION_LABELS.keys())
        current_conv = thesis.get("conviction", "MEDIUM") if thesis else "MEDIUM"
        conv_idx = conviction_options.index(current_conv) if current_conv in conviction_options else 1
        conviction = st.selectbox(
            "Convicção", conviction_options,
            index=conv_idx,
            format_func=lambda x: CONVICTION_LABELS[x],
        )

    with fc2:
        moat_options = list(MOAT_LABELS.keys())
        current_moat = thesis.get("moat_rating", "MODERATE") if thesis else "MODERATE"
        moat_idx = moat_options.index(current_moat) if current_moat in moat_options else 1
        moat_rating = st.selectbox(
            "Moat", moat_options,
            index=moat_idx,
            format_func=lambda x: MOAT_LABELS[x],
        )

        trend_options = list(MOAT_TREND_LABELS.keys())
        current_trend = thesis.get("moat_trend", "STABLE") if thesis else "STABLE"
        trend_idx = trend_options.index(current_trend) if current_trend in trend_options else 1
        moat_trend = st.selectbox(
            "Tendência Moat", trend_options,
            index=trend_idx,
            format_func=lambda x: MOAT_TREND_LABELS[x],
        )

    summary = st.text_area("Resumo da Tese", value=thesis.get("summary", "") if thesis else "", height=100)

    vc1, vc2, vc3 = st.columns(3)
    bull_val = float(thesis.get("bull_case_price") or 0) if thesis else 0.0
    base_val = float(thesis.get("base_case_price") or 0) if thesis else 0.0
    bear_val = float(thesis.get("bear_case_price") or 0) if thesis else 0.0
    with vc1:
        bull = st.number_input("Bull Case (R$)", value=bull_val, min_value=0.0, step=0.01)
    with vc2:
        base_price = st.number_input("Base Case (R$)", value=base_val, min_value=0.0, step=0.01)
    with vc3:
        bear = st.number_input("Bear Case (R$)", value=bear_val, min_value=0.0, step=0.01)

    rc1, rc2 = st.columns(2)
    with rc1:
        roic = st.number_input("ROIC (%)", value=float(thesis.get("roic_current") or 0) if thesis else 0.0, step=0.1)
    with rc2:
        wacc = st.number_input("WACC (%)", value=float(thesis.get("wacc_estimated") or 0) if thesis else 0.0, step=0.1)

    dc1, dc2 = st.columns(2)
    with dc1:
        next_review_val = thesis.get("next_review") if thesis else None
        if next_review_val:
            next_review = st.date_input("Próxima Revisão", value=date.fromisoformat(next_review_val))
        else:
            next_review = st.date_input("Próxima Revisão", value=date.today() + timedelta(days=90))
    with dc2:
        review_trigger = st.text_input("Trigger de Revisão", value=thesis.get("review_trigger", "") if thesis else "")

    # Kill switches como texto (um por linha) — Task 2.4
    ks_text = "\n".join(thesis.get("kill_switches") or []) if thesis else ""
    kill_switches_text = st.text_area(
        "Kill Switches (um por linha)", value=ks_text, height=80,
        help="Condições que invalidam a tese. Uma por linha.",
    )

    notes = st.text_area("Notas", value=thesis.get("notes", "") if thesis else "", height=60)

    submitted = st.form_submit_button("💾 Salvar Tese")

if submitted:
    target_price = _calc_target_price(bull, base_price, bear)
    kill_switches_list = [line.strip() for line in kill_switches_text.split("\n") if line.strip()]

    # Buscar position_id
    position_id = position["id"] if position else None

    thesis_data = {
        "ticker": selected_ticker,
        "position_id": position_id,
        "status": status,
        "conviction": conviction,
        "summary": summary,
        "moat_rating": moat_rating,
        "moat_trend": moat_trend,
        "bull_case_price": bull or None,
        "base_case_price": base_price or None,
        "bear_case_price": bear or None,
        "target_price": target_price,
        "roic_current": roic or None,
        "wacc_estimated": wacc or None,
        "kill_switches": kill_switches_list,
        "next_review": str(next_review),
        "review_trigger": review_trigger,
        "notes": notes,
    }

    if thesis:
        update_row("theses", thesis["id"], thesis_data)
        st.success(f"Tese de {selected_ticker} atualizada!")
    else:
        insert_row("theses", thesis_data)
        st.success(f"Tese de {selected_ticker} criada!")
    st.rerun()

# Botão de exclusão fora do form
if thesis:
    if st.button("🗑️ Excluir Tese", type="secondary"):
        delete_row("theses", thesis["id"])
        st.success(f"Tese de {selected_ticker} excluída.")
        st.rerun()

# ============================================================
# Catalisadores do ticker (2.3)
# ============================================================

st.markdown("---")
st.subheader(f"Catalisadores — {selected_ticker}")

catalysts = get_catalysts_by_ticker(selected_ticker)
if catalysts:
    for cat in catalysts:
        cc1, cc2, cc3 = st.columns([4, 1, 1])
        with cc1:
            completed = "✅" if cat.get("completed") else "⏳"
            impact_label = IMPACT_LABELS.get(cat.get("impact", ""), "")
            st.markdown(f"{completed} **{cat['description']}** — {cat.get('expected_date', '?')} ({impact_label})")
        with cc2:
            if not cat.get("completed"):
                if st.button("✅ Concluir", key=f"complete_{cat['id']}"):
                    update_row("catalysts", cat["id"], {"completed": True})
                    st.rerun()
        with cc3:
            if st.button("🗑️", key=f"del_cat_{cat['id']}"):
                delete_row("catalysts", cat["id"])
                st.rerun()
else:
    st.caption("Nenhum catalisador registrado.")

# Formulário para novo catalisador
with st.expander("➕ Adicionar Catalisador"):
    with st.form(f"new_catalyst_{selected_ticker}"):
        nc1, nc2 = st.columns(2)
        with nc1:
            cat_desc = st.text_input("Descrição")
            cat_date = st.date_input("Data esperada", value=date.today() + timedelta(days=30))
        with nc2:
            cat_impact = st.selectbox("Impacto", list(IMPACT_LABELS.keys()), format_func=lambda x: IMPACT_LABELS[x])
            cat_category = st.selectbox(
                "Categoria", list(CATALYST_CATEGORIES.keys()),
                format_func=lambda x: CATALYST_CATEGORIES[x],
            )
        if st.form_submit_button("Adicionar"):
            if cat_desc:
                insert_row("catalysts", {
                    "ticker": selected_ticker,
                    "description": cat_desc,
                    "expected_date": str(cat_date),
                    "impact": cat_impact,
                    "category": cat_category,
                    "completed": False,
                })
                st.success("Catalisador adicionado!")
                st.rerun()

# ============================================================
# Catalyst Timeline (2.5)
# ============================================================

st.markdown("---")
st.subheader("Catalyst Timeline (próximos 90 dias)")

all_catalysts = get_all_catalysts(include_completed=False)
if all_catalysts:
    timeline_data = []
    for cat in all_catalysts:
        if cat.get("expected_date"):
            timeline_data.append({
                "Ticker": cat["ticker"],
                "Descrição": cat["description"],
                "Data": cat["expected_date"],
                "Impacto": IMPACT_LABELS.get(cat.get("impact", ""), "—"),
                "Categoria": CATALYST_CATEGORIES.get(cat.get("category", ""), "—"),
            })
    if timeline_data:
        import pandas as pd

        df_timeline = pd.DataFrame(timeline_data)
        df_timeline["Data"] = pd.to_datetime(df_timeline["Data"])
        color_map = {"Alto": "#d62728", "Médio": "#ff7f0e", "Baixo": "#2ca02c"}
        fig = px.scatter(
            df_timeline, x="Data", y="Ticker",
            color="Impacto", color_discrete_map=color_map,
            hover_data=["Descrição", "Categoria"],
            size_max=12,
        )
        fig.update_traces(marker=dict(size=14))
        fig.update_layout(
            height=max(200, len(df_timeline["Ticker"].unique()) * 50 + 100),
            margin=dict(t=30, b=30),
            xaxis_title="",
            yaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum catalisador futuro registrado.")
else:
    st.info("Nenhum catalisador futuro registrado.")
