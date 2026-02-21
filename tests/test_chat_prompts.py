"""Testes para data/chat_prompts.py — prompts, context e intent detection."""

from unittest.mock import patch

from data.chat_prompts import (
    SYSTEM_PROMPT,
    _detect_tickers,
    build_context_for_message,
    build_extraction_prompt,
    build_portfolio_context,
    build_position_extraction_prompt,
    detect_position_update_intent,
    detect_save_intent,
)

# ============================================================
# SYSTEM_PROMPT
# ============================================================


class TestSystemPrompt:
    def test_not_empty(self):
        assert len(SYSTEM_PROMPT) > 100

    def test_contains_garp(self):
        assert "GARP" in SYSTEM_PROMPT

    def test_contains_cio_persona(self):
        assert "Comitê de Investimentos" in SYSTEM_PROMPT


# ============================================================
# _detect_tickers
# ============================================================


class TestDetectTickers:
    def test_br_ticker(self):
        result = _detect_tickers("Como está a INBR32?")
        assert "INBR32" in result

    def test_us_ticker(self):
        result = _detect_tickers("Preciso analisar NVDA")
        assert "NVDA" in result

    def test_multiple_tickers(self):
        result = _detect_tickers("Compare INBR32 com NVDA e ENGI4")
        assert "INBR32" in result
        assert "NVDA" in result
        assert "ENGI4" in result

    def test_no_tickers(self):
        result = _detect_tickers("Como está o mercado?")
        assert result == []

    def test_case_insensitive(self):
        result = _detect_tickers("e a nvda?")
        assert "NVDA" in result


# ============================================================
# detect_save_intent
# ============================================================


class TestDetectSaveIntent:
    def test_salvar(self):
        assert detect_save_intent("Pode salvar essa tese?") is True

    def test_gravar(self):
        assert detect_save_intent("Gravar análise no banco") is True

    def test_registrar(self):
        assert detect_save_intent("Registrar essa análise") is True

    def test_persistir(self):
        assert detect_save_intent("Persistir dados") is True

    def test_guardar(self):
        assert detect_save_intent("Guardar tese") is True

    def test_no_intent(self):
        assert detect_save_intent("Como está a INBR32?") is False

    def test_salvar_tese(self):
        assert detect_save_intent("Quero salvar a tese da INBR32") is True

    def test_empty_string(self):
        assert detect_save_intent("") is False


# ============================================================
# detect_position_update_intent
# ============================================================


class TestDetectPositionUpdateIntent:
    def test_comprei(self):
        assert detect_position_update_intent("Comprei 100 ações de INBR32") is True

    def test_vendi(self):
        assert detect_position_update_intent("Vendi 50 NVDA") is True

    def test_comprar(self):
        assert detect_position_update_intent("Vou comprar ENGI4") is True

    def test_atualizar_carteira(self):
        assert detect_position_update_intent("Atualizar carteira") is True

    def test_dividendo(self):
        assert detect_position_update_intent("Recebi dividendo de INBR32") is True

    def test_provento(self):
        assert detect_position_update_intent("Provento recebido") is True

    def test_trade(self):
        assert detect_position_update_intent("Fiz um trade hoje") is True

    def test_no_intent(self):
        assert detect_position_update_intent("Qual o preço-alvo da NVDA?") is False


# ============================================================
# build_portfolio_context
# ============================================================


class TestBuildPortfolioContext:
    @patch("data.chat_prompts.fetch_all")
    @patch("data.chat_prompts.get_all_thesis_summaries")
    def test_with_positions(self, mock_theses, mock_fetch_all):
        mock_fetch_all.side_effect = [
            [{"ticker": "INBR32", "quantity": 1905, "avg_price": 32.67, "total_invested": 62244, "is_active": True}],
            [],  # catalysts
        ]
        mock_theses.return_value = [
            {
                "ticker": "INBR32", "status": "GREEN", "conviction": "HIGH",
                "target_price": 58.0, "summary": "Banco digital",
            }
        ]
        result = build_portfolio_context()
        assert "INBR32" in result
        assert "Posições ativas" in result

    @patch("data.chat_prompts.fetch_all")
    @patch("data.chat_prompts.get_all_thesis_summaries")
    def test_empty_portfolio(self, mock_theses, mock_fetch_all):
        mock_fetch_all.return_value = []
        mock_theses.return_value = []
        result = build_portfolio_context()
        assert "Contexto do Portfólio" in result

    @patch("data.chat_prompts.fetch_all")
    @patch("data.chat_prompts.get_all_thesis_summaries")
    def test_with_catalysts(self, mock_theses, mock_fetch_all):
        mock_fetch_all.side_effect = [
            [],  # positions
            [{"ticker": "MELI", "description": "Q4 Results", "expected_date": "2026-02-19", "completed": False}],
        ]
        mock_theses.return_value = []
        result = build_portfolio_context()
        assert "MELI" in result


# ============================================================
# build_context_for_message
# ============================================================


class TestBuildContextForMessage:
    @patch("data.chat_prompts.get_deep_dives_by_ticker")
    def test_with_ticker_mentioned(self, mock_dives):
        mock_dives.return_value = [
            {"version": 1, "date": "2026-02-18", "content_md": "Deep dive content for INBR32"}
        ]
        result = build_context_for_message("Como está a INBR32?")
        assert "INBR32" in result

    @patch("data.chat_prompts.get_deep_dives_by_ticker")
    def test_no_ticker_returns_empty(self, mock_dives):
        result = build_context_for_message("Como está o mercado?")
        assert result == ""

    @patch("data.chat_prompts.get_deep_dives_by_ticker")
    def test_truncates_long_content(self, mock_dives):
        mock_dives.return_value = [
            {"version": 1, "date": "2026-02-18", "content_md": "X" * 5000}
        ]
        result = build_context_for_message("Analise INBR32")
        assert "truncado" in result


# ============================================================
# build_extraction_prompt / build_position_extraction_prompt
# ============================================================


class TestBuildPrompts:
    def test_extraction_prompt_returns_string(self):
        result = build_extraction_prompt()
        assert "JSON" in result
        assert "ticker" in result

    def test_position_extraction_prompt_returns_string(self):
        result = build_position_extraction_prompt()
        assert "JSON" in result
        assert "BUY" in result
        assert "SELL" in result
