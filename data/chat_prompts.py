"""System prompts, contexto dinâmico e detecção de intent para o Assessor."""

import re

from data.db import (
    fetch_all,
    get_all_thesis_summaries,
    get_deep_dives_by_ticker,
)
from utils.constants import TICKER_SECTOR, TICKERS_ALL

# ============================================================
# System prompt estático (persona CIO + comitê)
# ============================================================

SYSTEM_PROMPT = """\
Você é o **Assessor do Comitê de Investimentos** de um family office \
pessoal (~R$514k, ~20 posições BR+US).

## Seu papel
- Coordenar análises de investimento como um CIO experiente
- Consultar o comitê de 5 analistas setoriais quando pertinente:
  - Analista de Energia & Materiais (BRAV3, SUZB3, KLBN4)
  - Analista de Utilities & Concessões (ENGI4, EQTL3)
  - Analista de Consumo/Varejo/Imobiliário (GMAT3, ALOS3, PLPL3, RAPT4)
  - Analista de Tech & Semicondutores (TSM, NVDA, ASML, MELI, GOOGL, SNPS, MU)
  - Analista Financeiro & Crédito (INBR32)

## Filosofia de investimento
- **GARP** — qualidade + crescimento a preço razoável
- Moat analysis (Morningstar + Mauboussin)
- Valuation: bull/base/bear (20/60/20), margem mínima 15% core / 25% tático
- Kill switches: condições que invalidam a tese
- Foco em ROIC vs WACC spread

## Regras de comportamento
- Responda em português. Termos técnicos em inglês quando consagrados.
- Relacione perguntas com deep dives e relatórios existentes.
- Cite dados concretos — não invente números.
- Se não tiver informação suficiente, diga claramente.
- Mencione status da tese e conviction ao discutir posições.
- Confirme o que será salvo quando o usuário pedir.
- Ao receber dados de posições, mostre tabela diff antes de confirmar.

## Busca na web
- Quando o usuário perguntar sobre notícias recentes, resultados trimestrais, releases, \
eventos de mercado ou dados que não estão no contexto do portfólio, use a ferramenta web_search.
- Cite as fontes (URLs) quando usar dados da busca.
- Use topic='finance' para ações e mercado, 'news' para notícias gerais.
- Use search_depth='advanced' apenas para pesquisas que exigem profundidade."""


def build_portfolio_context() -> str:
    """Build dynamic context string with current portfolio state."""
    lines = ["## Contexto do Portfólio (dados atuais)\n"]

    # Positions
    positions = fetch_all("positions")
    if positions:
        lines.append("### Posições ativas")
        for p in positions:
            if not p.get("is_active"):
                continue
            ticker = p.get("ticker", "?")
            qty = p.get("quantity", 0) or 0
            avg = p.get("avg_price", 0) or 0
            invested = p.get("total_invested", 0) or 0
            sector = TICKER_SECTOR.get(ticker, "?")
            lines.append(f"- **{ticker}** ({sector}): {qty} ações, PM {avg:.2f}, investido {invested:,.0f}")
        lines.append("")

    # Theses summaries
    theses = get_all_thesis_summaries()
    if theses:
        lines.append("### Teses de investimento")
        for t in theses:
            status_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}.get(t.get("status", ""), "⚪")
            conv = t.get("conviction", "?")
            target = t.get("target_price")
            target_str = f", target {target:.2f}" if target else ""
            summary = (t.get("summary") or "")[:150]
            lines.append(f"- {status_emoji} **{t['ticker']}** (conv: {conv}{target_str}): {summary}")
        lines.append("")

    # Upcoming catalysts
    catalysts = fetch_all("catalysts")
    upcoming = [c for c in catalysts if not c.get("completed")][:8]
    if upcoming:
        lines.append("### Próximos catalisadores")
        for c in upcoming:
            date = c.get("expected_date", "?")
            lines.append(f"- 📅 {date} — **{c.get('ticker', '?')}**: {c.get('description', '')}")
        lines.append("")

    return "\n".join(lines)


def build_context_for_message(user_message: str) -> str:
    """Detect tickers mentioned in user message and return relevant deep dive content."""
    mentioned = _detect_tickers(user_message)
    if not mentioned:
        return ""

    parts = [f"## Deep dives relevantes (tickers mencionados: {', '.join(mentioned)})\n"]
    for ticker in mentioned[:3]:  # Limit to 3 to avoid token explosion
        dives = get_deep_dives_by_ticker(ticker)
        if dives:
            latest = dives[0]
            content = latest.get("content_md", "")
            # Truncate very long deep dives to ~4000 chars
            if len(content) > 4000:
                content = content[:4000] + "\n\n[... conteúdo truncado ...]"
            parts.append(f"### {ticker} (v{latest.get('version', 1)}, {latest.get('date', '?')})")
            parts.append(content)
            parts.append("")
    return "\n".join(parts)


def detect_save_intent(user_message: str) -> bool:
    """Detect if user wants to save analysis/thesis from conversation."""
    patterns = [
        r"\bsalvar?\b",
        r"\bsalve\b",
        r"\bgravar?\b",
        r"\bregistrar?\b",
        r"\bpersistir?\b",
        r"\bguardar?\b",
        r"\bsalvar?\s+(tese|an[aá]lise|deep\s*dive)\b",
    ]
    msg_lower = user_message.lower()
    return any(re.search(p, msg_lower) for p in patterns)


def detect_position_update_intent(user_message: str) -> bool:
    """Detect if user wants to update portfolio positions."""
    patterns = [
        r"\bcomprei\b",
        r"\bvendi\b",
        r"\bcomprar?\b",
        r"\bvender?\b",
        r"\batualizar?\s+(posi[çc][õo]|carteira|portf[oó]lio)\b",
        r"\bopera[çc][ãa]o\b",
        r"\btrade\b",
        r"\bdividendo\b",
        r"\bprovento\b",
    ]
    msg_lower = user_message.lower()
    return any(re.search(p, msg_lower) for p in patterns)


def build_extraction_prompt() -> str:
    """Build prompt for extracting structured thesis data from conversation."""
    return """Analise a conversa abaixo e extraia os dados estruturados da tese de investimento discutida.

Retorne APENAS um JSON válido no seguinte formato (omita campos não discutidos):

```json
{
    "ticker": "TICKER",
    "status": "GREEN|YELLOW|RED",
    "conviction": "HIGH|MEDIUM|LOW",
    "summary": "Resumo da tese em 3-5 linhas",
    "moat_rating": "STRONG|MODERATE|WEAK|NONE",
    "moat_trend": "WIDENING|STABLE|NARROWING",
    "bull_case_price": 0.0,
    "base_case_price": 0.0,
    "bear_case_price": 0.0,
    "target_price": 0.0,
    "roic_current": 0.0,
    "wacc_estimated": 0.0,
    "growth_drivers": ["driver1", "driver2"],
    "kill_switches": ["switch1", "switch2"],
    "catalysts": [{"description": "desc", "expected_date": "YYYY-MM-DD", "impact": "HIGH|MEDIUM|LOW"}]
}
```

Se a conversa não contém dados suficientes para uma tese, retorne `null`."""


def build_position_extraction_prompt() -> str:
    """Build prompt for extracting position updates from text/images."""
    return """Analise o conteúdo abaixo (texto ou dados extraídos de screenshot) e identifique operações de carteira.

Retorne APENAS um JSON válido no seguinte formato:

```json
{
    "operations": [
        {
            "type": "BUY|SELL|DIVIDEND",
            "ticker": "TICKER",
            "quantity": 0,
            "price": 0.0,
            "total_value": 0.0,
            "currency": "BRL|USD",
            "date": "YYYY-MM-DD",
            "notes": "observação opcional"
        }
    ]
}
```

Regras:
- Identifique TODOS os ativos mencionados, com ticker correto
- Para compras: type=BUY, quantity positiva
- Para vendas: type=SELL, quantity positiva (será subtraída)
- Para dividendos/proventos: type=DIVIDEND, total_value é o valor recebido
- Se não conseguir identificar operações, retorne {"operations": []}"""


def _detect_tickers(text: str) -> list[str]:
    """Detect tickers mentioned in text."""
    text_upper = text.upper()
    return [t for t in TICKERS_ALL if t.upper() in text_upper]
