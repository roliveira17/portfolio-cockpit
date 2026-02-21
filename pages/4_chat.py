"""Pagina Assessor — Chat com o Comite de Investimentos via OpenRouter."""

from datetime import date

import streamlit as st

from data.chat_prompts import (
    SYSTEM_PROMPT,
    build_context_for_message,
    build_extraction_prompt,
    build_portfolio_context,
    build_position_extraction_prompt,
    detect_position_update_intent,
    detect_save_intent,
)
from data.db import (
    fetch_all,
    get_all_thesis_summaries,
    get_deep_dives_by_ticker,
    get_position_by_ticker,
    insert_row,
    update_position_fields,
    upsert_thesis,
)
from data.llm import (
    build_vision_content,
    encode_image_to_base64,
    extract_structured_data,
    fetch_openrouter_credits,
    stream_chat_response,
)
from utils.constants import OPENROUTER_MODELS, THESIS_STATUS
from utils.formatting import fmt_date

# ============================================================
# Save / update helpers (must be defined before use)
# ============================================================


def _save_extracted_data(data: dict) -> None:
    """Save extracted thesis data to DB."""
    ticker = data.get("ticker", "")
    if not ticker:
        return

    thesis_fields = [
        "status",
        "conviction",
        "summary",
        "moat_rating",
        "moat_trend",
        "bull_case_price",
        "base_case_price",
        "bear_case_price",
        "target_price",
        "roic_current",
        "wacc_estimated",
        "growth_drivers",
        "kill_switches",
    ]
    thesis_data = {f: data[f] for f in thesis_fields if f in data and data[f] is not None}
    if thesis_data:
        upsert_thesis(ticker, thesis_data)

    for cat in data.get("catalysts", []):
        if cat.get("description"):
            insert_row(
                "catalysts",
                {
                    "ticker": ticker,
                    "description": cat["description"],
                    "expected_date": cat.get("expected_date"),
                    "impact": cat.get("impact", "MEDIUM"),
                    "category": "OTHER",
                    "completed": False,
                },
            )

    # Save conversation as deep dive
    summary_md = _build_conversation_summary()
    if summary_md:
        existing = get_deep_dives_by_ticker(ticker)
        next_version = max((d.get("version", 1) for d in existing), default=0) + 1
        insert_row(
            "deep_dives",
            {
                "ticker": ticker,
                "version": next_version,
                "title": f"Analise via Chat — {ticker}",
                "content_md": summary_md,
                "summary": data.get("summary", ""),
                "thesis_status_at_time": data.get("status", ""),
                "conviction_at_time": data.get("conviction", ""),
                "target_price_at_time": data.get("target_price"),
                "date": str(date.today()),
                "tags": ["chat_analysis"],
            },
        )


def _build_conversation_summary() -> str:
    """Build markdown summary from chat messages."""
    parts = ["# Analise via Chat\n"]
    for msg in st.session_state.get("chat_messages", []):
        role = "**Usuario:**" if msg["role"] == "user" else "**Assessor:**"
        content = msg["content"] if isinstance(msg["content"], str) else "[conteudo multipart]"
        parts.append(f"{role} {content}\n")
    return "\n".join(parts)


def _apply_position_updates(data: dict) -> None:
    """Apply position updates from extracted operations."""
    for op in data.get("operations", []):
        ticker = op.get("ticker", "")
        op_type = op.get("type", "")
        qty = op.get("quantity", 0)
        price = op.get("price", 0)
        total = op.get("total_value") or (qty * price if qty and price else 0)

        if not ticker or not op_type:
            continue

        insert_row(
            "transactions",
            {
                "ticker": ticker,
                "type": op_type,
                "quantity": qty,
                "price": price,
                "total_value": total,
                "currency": op.get("currency", "BRL"),
                "date": op.get("date", str(date.today())),
                "notes": op.get("notes", f"Via chat — {op_type}"),
            },
        )

        pos = get_position_by_ticker(ticker)
        if not pos:
            continue

        if op_type == "BUY" and qty > 0 and price > 0:
            old_qty = pos.get("quantity", 0) or 0
            old_invested = pos.get("total_invested", 0) or 0
            new_qty = old_qty + qty
            new_invested = old_invested + total
            update_position_fields(
                ticker,
                {
                    "quantity": new_qty,
                    "avg_price": new_invested / new_qty if new_qty > 0 else 0,
                    "total_invested": new_invested,
                },
            )
        elif op_type == "SELL" and qty > 0:
            old_qty = pos.get("quantity", 0) or 0
            new_qty = max(0, old_qty - qty)
            update_position_fields(
                ticker,
                {
                    "quantity": new_qty,
                    "total_invested": new_qty * (pos.get("avg_price", 0) or 0),
                },
            )
        elif op_type == "DIVIDEND" and total > 0:
            old_div = pos.get("dividends_received", 0) or 0
            update_position_fields(ticker, {"dividends_received": old_div + total})


# ============================================================
# Session state init
# ============================================================

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = list(OPENROUTER_MODELS.keys())[0]
if "pending_save" not in st.session_state:
    st.session_state["pending_save"] = None
if "pending_position_update" not in st.session_state:
    st.session_state["pending_position_update"] = None

# ============================================================
# Sidebar: Kanban compacto + catalisadores
# ============================================================

with st.sidebar:
    st.markdown("### Status das Teses")
    theses = get_all_thesis_summaries()

    for status_key, status_info in THESIS_STATUS.items():
        group = [t for t in theses if t.get("status") == status_key]
        if group:
            st.markdown(f"**{status_info['emoji']} {status_info['label']}**")
            for t in group:
                st.caption(f"  {t['ticker']} — Conv: {t.get('conviction', '?')}")

    if not theses:
        st.caption("Nenhuma tese cadastrada. Execute o seed.")

    st.markdown("---")
    st.markdown("### Proximos Catalisadores")
    catalysts = fetch_all("catalysts")
    upcoming = sorted(
        [c for c in catalysts if not c.get("completed")],
        key=lambda c: c.get("expected_date") or "9999",
    )[:5]
    for c in upcoming:
        d = fmt_date(c.get("expected_date"), short=True)
        st.caption(f"  📅 {d} — **{c.get('ticker', '?')}**: {c.get('description', '')}")
    if not upcoming:
        st.caption("Nenhum catalisador pendente.")

    st.markdown("---")
    if st.button("🔄 Nova conversa"):
        st.session_state["chat_messages"] = []
        st.session_state["pending_save"] = None
        st.session_state["pending_position_update"] = None
        st.session_state.pop("llm_usage", None)
        st.rerun()

    # ── Consumo API ──
    st.markdown("---")
    st.markdown("### Consumo API")
    usage = st.session_state.get("llm_usage", {})
    total_tokens = usage.get("total_tokens", 0)
    request_count = usage.get("request_count", 0)

    col1, col2 = st.columns(2)
    if total_tokens >= 1_000_000:
        col1.metric("Tokens", f"{total_tokens / 1_000_000:.1f}M")
    elif total_tokens >= 1_000:
        col1.metric("Tokens", f"{total_tokens / 1_000:.1f}K")
    else:
        col1.metric("Tokens", str(total_tokens))
    col2.metric("Requests", str(request_count))

    total_cost = usage.get("total_cost_usd", 0.0)
    st.metric("Custo sessao", f"${total_cost:.4f}")

    try:
        credits = fetch_openrouter_credits()
        if credits:
            total_credits = credits["total_credits"]
            total_usage = credits["total_usage"]
            remaining = total_credits - total_usage
            st.metric("Saldo conta", f"${remaining:.2f}")
            if total_credits > 0:
                st.progress(min(remaining / total_credits, 1.0))
    except Exception:
        pass

# ============================================================
# Main area: Model selector + image upload
# ============================================================

st.header("💬 Assessor — Comite de Investimentos")

top1, top2 = st.columns([3, 2])
with top1:
    model_key = st.selectbox(
        "Modelo",
        list(OPENROUTER_MODELS.keys()),
        index=list(OPENROUTER_MODELS.keys()).index(st.session_state["selected_model"]),
        key="model_selector",
    )
    st.session_state["selected_model"] = model_key
with top2:
    uploaded_image = None
    if OPENROUTER_MODELS[model_key].get("supports_vision"):
        uploaded_image = st.file_uploader(
            "📎 Anexar imagem",
            type=["png", "jpg", "jpeg", "webp"],
            key="chat_image_upload",
        )
    else:
        st.caption("Modelo nao suporta imagens.")

# ============================================================
# Pending save confirmation
# ============================================================

if st.session_state["pending_save"] is not None:
    st.info("**Dados extraidos para salvar:**")
    st.json(st.session_state["pending_save"])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Confirmar e salvar", key="confirm_save"):
            _save_extracted_data(st.session_state["pending_save"])
            st.session_state["pending_save"] = None
            st.success("Dados salvos com sucesso!")
            st.rerun()
    with c2:
        if st.button("❌ Cancelar", key="cancel_save"):
            st.session_state["pending_save"] = None
            st.rerun()

# ============================================================
# Pending position update confirmation
# ============================================================

if st.session_state["pending_position_update"] is not None:
    st.info("**Operacoes detectadas:**")
    st.json(st.session_state["pending_position_update"])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Confirmar atualizacao", key="confirm_pos"):
            _apply_position_updates(st.session_state["pending_position_update"])
            st.session_state["pending_position_update"] = None
            st.success("Posicoes atualizadas!")
            st.rerun()
    with c2:
        if st.button("❌ Cancelar", key="cancel_pos"):
            st.session_state["pending_position_update"] = None
            st.rerun()

# ============================================================
# Chat history display
# ============================================================

for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        content = msg["content"]
        if isinstance(content, str):
            st.markdown(content)
        else:
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    st.markdown(part["text"])
                elif isinstance(part, dict) and part.get("type") == "image_url":
                    st.caption("🖼️ [imagem anexada]")

# ============================================================
# Chat input
# ============================================================

if prompt := st.chat_input("Pergunte ao comite de investimentos..."):
    # Build user content (text or multipart with image)
    if uploaded_image is not None:
        img_b64 = encode_image_to_base64(uploaded_image)
        mime = uploaded_image.type or "image/png"
        user_content = build_vision_content(prompt, img_b64, mime)
    else:
        user_content = prompt

    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_image is not None:
            st.caption("🖼️ [imagem anexada]")

    st.session_state["chat_messages"].append({"role": "user", "content": user_content})

    # Build system message with dynamic context
    system_content = SYSTEM_PROMPT + "\n\n" + build_portfolio_context()
    ticker_ctx = build_context_for_message(prompt)
    if ticker_ctx:
        system_content += "\n\n" + ticker_ctx

    api_messages = [{"role": "system", "content": system_content}]
    api_messages.extend(st.session_state["chat_messages"])

    with st.chat_message("assistant"):
        response_text = st.write_stream(stream_chat_response(api_messages, model_key))

    st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})

    # Detect save intent
    if detect_save_intent(prompt):
        extracted = extract_structured_data(st.session_state["chat_messages"], model_key, build_extraction_prompt())
        if extracted and extracted.get("ticker"):
            st.session_state["pending_save"] = extracted
            st.rerun()

    # Detect position update intent
    if detect_position_update_intent(prompt) or uploaded_image is not None:
        msgs = st.session_state["chat_messages"]
        extracted = extract_structured_data(msgs, model_key, build_position_extraction_prompt())
        if extracted and extracted.get("operations"):
            st.session_state["pending_position_update"] = extracted
            st.rerun()
