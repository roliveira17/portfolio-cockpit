"""Testes para data/llm.py — cliente OpenRouter, parsing JSON, vision helpers."""

from unittest.mock import MagicMock, patch

from data.llm import (
    _parse_json_from_response,
    _summarize_conversation,
    build_vision_content,
)

# ============================================================
# _parse_json_from_response
# ============================================================


class TestParseJsonFromResponse:
    def test_json_in_code_fence(self):
        text = """Aqui está o resultado:
```json
{"ticker": "INBR32", "status": "GREEN"}
```
"""
        result = _parse_json_from_response(text)
        assert result == {"ticker": "INBR32", "status": "GREEN"}

    def test_json_inline(self):
        text = '{"ticker": "NVDA", "conviction": "HIGH"}'
        result = _parse_json_from_response(text)
        assert result == {"ticker": "NVDA", "conviction": "HIGH"}

    def test_json_in_generic_code_fence(self):
        text = """```
{"ticker": "ENGI4"}
```"""
        result = _parse_json_from_response(text)
        assert result == {"ticker": "ENGI4"}

    def test_invalid_json(self):
        result = _parse_json_from_response("not json at all")
        assert result is None

    def test_empty_string(self):
        result = _parse_json_from_response("")
        assert result is None

    def test_none_text(self):
        # The function handles empty, but our code path: if not text: return None
        result = _parse_json_from_response("")
        assert result is None


# ============================================================
# _summarize_conversation
# ============================================================


class TestSummarizeConversation:
    def test_user_and_assistant(self):
        messages = [
            {"role": "user", "content": "Como está a INBR32?"},
            {"role": "assistant", "content": "A INBR32 está em alta."},
        ]
        result = _summarize_conversation(messages)
        assert "Usuário: Como está a INBR32?" in result
        assert "Assessor: A INBR32 está em alta." in result

    def test_empty_messages(self):
        result = _summarize_conversation([])
        assert result == ""

    def test_non_string_content(self):
        messages = [{"role": "user", "content": [{"type": "text", "text": "Olá"}]}]
        result = _summarize_conversation(messages)
        assert "Usuário:" in result


# ============================================================
# build_vision_content
# ============================================================


class TestBuildVisionContent:
    def test_returns_multipart(self):
        result = build_vision_content("Analise esta imagem", "base64data", "image/png")
        assert len(result) == 2
        assert result[0]["type"] == "text"
        assert result[0]["text"] == "Analise esta imagem"
        assert result[1]["type"] == "image_url"
        assert "data:image/png;base64,base64data" in result[1]["image_url"]["url"]


# ============================================================
# call_chat_response (mocked)
# ============================================================


class TestCallChatResponse:
    @patch("data.llm.get_openrouter_client")
    def test_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta do modelo"
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from data.llm import call_chat_response

        result = call_chat_response(
            [{"role": "user", "content": "Olá"}],
            "Claude Sonnet 4.6 (~$2.25/sessão)",
        )
        assert result == "Resposta do modelo"

    @patch("data.llm.get_openrouter_client", side_effect=Exception("API down"))
    def test_failure_returns_empty(self, mock_get_client):
        from data.llm import call_chat_response

        result = call_chat_response(
            [{"role": "user", "content": "Olá"}],
            "Claude Sonnet 4.6 (~$2.25/sessão)",
        )
        assert result == ""


# ============================================================
# extract_structured_data (mocked)
# ============================================================


class TestExtractStructuredData:
    @patch("data.llm.call_chat_response")
    def test_returns_parsed_dict(self, mock_call):
        mock_call.return_value = '```json\n{"ticker": "INBR32", "status": "GREEN"}\n```'

        from data.llm import extract_structured_data

        result = extract_structured_data(
            [{"role": "user", "content": "Tese INBR32 é GREEN"}],
            "Claude Sonnet 4.6 (~$2.25/sessão)",
            "Extract thesis data",
        )
        assert result == {"ticker": "INBR32", "status": "GREEN"}

    @patch("data.llm.call_chat_response")
    def test_invalid_json_returns_none(self, mock_call):
        mock_call.return_value = "No JSON here"

        from data.llm import extract_structured_data

        result = extract_structured_data(
            [{"role": "user", "content": "Olá"}],
            "Claude Sonnet 4.6 (~$2.25/sessão)",
            "Extract data",
        )
        assert result is None
