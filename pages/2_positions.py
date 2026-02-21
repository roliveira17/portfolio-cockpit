"""Página Positions — Visão detalhada de cada posição."""

from datetime import date

import streamlit as st

from analytics.portfolio import build_portfolio_df
from data.db import get_positions, get_theses, insert_row
from data.market_data import fetch_all_quotes, fetch_batch_price_history
from utils.cache_info import record_fetch_time, show_freshness_badge
from utils.constants import TICKERS_BR, TICKERS_US
from utils.formatting import fmt_brl, fmt_pct, fmt_usd

st.header("💼 Positions")


# ============================================================
# Helper: Botão Analisar (análise IA rápida)
# ============================================================


def _show_analyze_button(row, theses_map: dict) -> None:
    """Exibe botão 'Analisar' que gera análise IA rápida da posição."""
    if st.button(f"🤖 Analisar {row['ticker']}", key=f"analyze_{row['ticker']}"):
        try:
            from data.llm import stream_chat_response
            from utils.constants import OPENROUTER_MODELS

            thesis = theses_map.get(row["ticker"], {})
            fmt_fn = fmt_brl if row["currency"] == "BRL" else fmt_usd

            context = (
                f"Ticker: {row['ticker']} ({row['company_name']})\n"
                f"Setor: {row['sector']} | Mercado: {row['market']}\n"
                f"Preço Atual: {fmt_fn(row['current_price'])}\n"
                f"Preço Médio: {fmt_fn(row['avg_price'])}\n"
                f"P&L: {fmt_pct(row['pnl_pct'], sign=True)}\n"
                f"Peso: {row['weight']:.1f}% (target: {row['target_weight']:.1f}%)\n"
            )
            if thesis:
                context += (
                    f"Tese: {thesis.get('status', '?')} | Convicção: {thesis.get('conviction', '?')}\n"
                    f"Target Price: {thesis.get('target_price', '?')}\n"
                    f"ROIC: {thesis.get('roic_current', '?')}% | WACC: {thesis.get('wacc_estimated', '?')}%\n"
                )

            prompt = (
                "Você é um analista GARP (Growth at Reasonable Price). "
                "Faça uma análise rápida (3-5 parágrafos) da posição abaixo, "
                "considerando: valuation, momentum, riscos e recomendação de ação.\n\n"
                f"{context}"
            )

            messages = [
                {"role": "system", "content": "Responda em português, de forma concisa e acionável."},
                {"role": "user", "content": prompt},
            ]

            model_key = next(
                (k for k in OPENROUTER_MODELS if "Flash" in k or "mini" in k or "Haiku" in k),
                list(OPENROUTER_MODELS.keys())[0],
            )

            with st.spinner("Analisando..."):
                st.write_stream(stream_chat_response(messages, model_key))

        except Exception as e:
            st.warning(f"Análise IA indisponível: {e}")


# --- Carregar dados ---
positions = get_positions(active_only=True)
if not positions:
    st.warning("Não foi possível carregar posições. Verifique a conexão com o Supabase.")
    st.stop()
quotes = fetch_all_quotes()
record_fetch_time("quotes")
df = build_portfolio_df(positions, quotes)

# --- Sparklines: histórico 30d ---
price_hist = fetch_batch_price_history(tickers_br=TICKERS_BR, tickers_us=TICKERS_US, period="1mo")
spark_map = {}
if price_hist is not None:
    for col in price_hist.columns:
        vals = price_hist[col].dropna().tolist()
        spark_map[col] = vals[-20:] if len(vals) > 20 else vals
df["spark"] = df["ticker"].apply(lambda t: spark_map.get(t, []))

# --- Theses para filtro de revisão vencida ---
theses = get_theses() or []
theses_by_ticker = {t["ticker"]: t for t in theses}

# ============================================================
# Filtros
# ============================================================

show_freshness_badge("quotes", "Cotações")

col_f1, col_f2 = st.columns(2)
with col_f1:
    sectors = ["Todos"] + sorted(df["sector"].unique().tolist())
    selected_sector = st.selectbox("Filtro Setor", sectors)
with col_f2:
    markets = ["Todos", "BR", "US"]
    selected_market = st.selectbox("Filtro Mercado", markets)

# --- Filtros rápidos preset ---
st.markdown("**Filtros rápidos:**")
preset_cols = st.columns(5)
preset = None
with preset_cols[0]:
    if st.button("Todos", use_container_width=True):
        preset = "all"
with preset_cols[1]:
    if st.button("Overweight", use_container_width=True):
        preset = "over"
with preset_cols[2]:
    if st.button("Underweight", use_container_width=True):
        preset = "under"
with preset_cols[3]:
    if st.button("Top P&L", use_container_width=True):
        preset = "top_pnl"
with preset_cols[4]:
    if st.button("Rev. Vencida", use_container_width=True):
        preset = "overdue"

filtered = df.copy()
if selected_sector != "Todos":
    filtered = filtered[filtered["sector"] == selected_sector]
if selected_market != "Todos":
    filtered = filtered[filtered["market"] == selected_market]

# Aplicar preset
if preset == "over":
    filtered = filtered[filtered["weight_gap"] > 0.5]
elif preset == "under":
    filtered = filtered[filtered["weight_gap"] < -0.5]
elif preset == "top_pnl":
    filtered = filtered.nlargest(5, "pnl_pct")
elif preset == "overdue":
    today = str(date.today())
    overdue_tickers = {t["ticker"] for t in theses if t.get("next_review") and t["next_review"] < today}
    filtered = filtered[filtered["ticker"].isin(overdue_tickers)]

# ============================================================
# Tabela Principal (com sparklines via column_config)
# ============================================================

st.subheader(f"Posições ({len(filtered)})")

display_cols = [
    "ticker",
    "company_name",
    "sector",
    "weight",
    "target_weight",
    "weight_gap",
    "current_price",
    "avg_price",
    "pnl_pct",
    "change_pct",
    "spark",
]
display_df = filtered[display_cols].copy()

st.dataframe(
    display_df,
    column_config={
        "ticker": st.column_config.TextColumn("Ticker"),
        "company_name": st.column_config.TextColumn("Empresa"),
        "sector": st.column_config.TextColumn("Setor"),
        "weight": st.column_config.NumberColumn("Peso %", format="%.1f"),
        "target_weight": st.column_config.NumberColumn("Target %", format="%.1f"),
        "weight_gap": st.column_config.NumberColumn("Gap %", format="%+.1f"),
        "current_price": st.column_config.NumberColumn("Preço", format="%.2f"),
        "avg_price": st.column_config.NumberColumn("PM", format="%.2f"),
        "pnl_pct": st.column_config.NumberColumn("P&L %", format="%+.1f"),
        "change_pct": st.column_config.NumberColumn("Dia %", format="%+.2f"),
        "spark": st.column_config.LineChartColumn("30d", width="small"),
    },
    use_container_width=True,
    hide_index=True,
    height=min(35 * len(display_df) + 38, 600),
)

# ============================================================
# Detalhes da posição selecionada
# ============================================================

st.markdown("---")
st.subheader("Detalhes da Posição")

tickers = filtered["ticker"].tolist()
if tickers:
    selected_ticker = st.selectbox("Selecionar posição", tickers)
    row = filtered[filtered["ticker"] == selected_ticker].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{row['ticker']}** — {row['company_name']}")
        st.markdown(f"Setor: {row['sector']} | Mercado: {row['market']}")
        st.markdown(f"Quantidade: {row['quantity']:,.2f}")
        fmt_fn = fmt_brl if row["currency"] == "BRL" else fmt_usd
        st.markdown(f"Preço Médio: {fmt_fn(row['avg_price'])}")
        st.markdown(f"Preço Atual: {fmt_fn(row['current_price'])}")

    with col2:
        st.markdown("**P&L**")
        st.markdown(f"Investido: {fmt_fn(row['total_invested'])}")
        if row["current_value_original"]:
            st.markdown(f"Valor Atual: {fmt_fn(row['current_value_original'])}")
        st.markdown(f"P&L: {fmt_pct(row['pnl_pct'], sign=True)}")
        if row["dividends_received"] > 0:
            st.markdown(f"Dividendos: {fmt_fn(row['dividends_received'])}")
            st.markdown(f"P&L c/ Div: {fmt_pct(row['pnl_with_div_pct'], sign=True)}")

    with col3:
        st.markdown("**Alocação**")
        st.markdown(f"Peso Atual: {row['weight']:.1f}%")
        st.markdown(f"Peso Target: {row['target_weight']:.1f}%")
        gap = row["weight_gap"]
        gap_label = "overweight" if gap > 0 else "underweight" if gap < 0 else "on target"
        st.markdown(f"Gap: {gap:+.1f}% ({gap_label})")

    # --- Botão "Analisar" (análise IA rápida) ---
    _show_analyze_button(row, theses_by_ticker)

# ============================================================
# Registro de Transações
# ============================================================

st.markdown("---")
st.subheader("Registrar Transação")

with st.expander("➕ Nova Transação"):
    with st.form("new_transaction"):
        tx_tickers = df[df["sector"] != "caixa"]["ticker"].tolist()
        tc1, tc2 = st.columns(2)
        with tc1:
            tx_ticker = st.selectbox("Ticker", tx_tickers, key="tx_ticker")
            tx_type = st.selectbox("Tipo", ["BUY", "SELL", "DIVIDEND"])
            tx_date = st.date_input("Data", value=date.today())
        with tc2:
            tx_qty = st.number_input("Quantidade", min_value=0.0, step=1.0)
            tx_price = st.number_input("Preço", min_value=0.0, step=0.01)
            tx_notes = st.text_input("Observações")

        if st.form_submit_button("Registrar"):
            if tx_qty > 0 and (tx_price > 0 or tx_type == "DIVIDEND"):
                pos = next((p for p in positions if p["ticker"] == tx_ticker), None)
                total_value = tx_qty * tx_price
                tx_data = {
                    "position_id": pos["id"] if pos else None,
                    "ticker": tx_ticker,
                    "type": tx_type,
                    "quantity": tx_qty,
                    "price": tx_price,
                    "total_value": total_value,
                    "currency": pos["currency"] if pos else "BRL",
                    "date": str(tx_date),
                    "notes": tx_notes,
                }
                try:
                    insert_row("transactions", tx_data)
                    st.success(f"Transação {tx_type} de {tx_ticker} registrada!")
                except Exception:
                    st.error("Erro ao registrar transação.")
            else:
                st.warning("Quantidade e preço devem ser positivos.")

# ============================================================
# Export CSV
# ============================================================

st.markdown("---")
csv = filtered.drop(columns=["spark"], errors="ignore").to_csv(index=False)
st.download_button("📥 Exportar CSV", csv, "positions.csv", "text/csv")
