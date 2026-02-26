"""Testes para data/llm.py — cliente OpenRouter, parsing JSON, vision helpers, usage tracking."""

from unittest.mock import MagicMock, patch

from data.llm import (
    _parse_json_from_response,
    _summarize_conversation,
    _track_usage_from_response,
    build_vision_content,
    calculate_cost,
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


# ============================================================
# fetch_openrouter_credits
# ============================================================


class TestFetchOpenRouterCredits:
    @patch("data.llm.requests.get")
    @patch("data.llm.st.secrets", {"openrouter": {"api_key": "test-key"}})
    def test_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": {"total_credits": 10.0, "total_usage": 3.5}}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from data.llm import fetch_openrouter_credits

        result = fetch_openrouter_credits.__wrapped__()
        assert result == {"total_credits": 10.0, "total_usage": 3.5}
        mock_get.assert_called_once()

    @patch("data.llm.requests.get", side_effect=Exception("Network error"))
    @patch("data.llm.st.secrets", {"openrouter": {"api_key": "test-key"}})
    def test_error_returns_none(self, mock_get):
        from data.llm import fetch_openrouter_credits

        result = fetch_openrouter_credits.__wrapped__()
        assert result is None


# ============================================================
# calculate_cost
# ============================================================


class TestCalculateCost:
    def test_known_model(self):
        # Claude Sonnet: input=3.0/1M, output=15.0/1M
        cost = calculate_cost("anthropic/claude-sonnet-4-20250514", 1000, 500)
        expected = (1000 / 1_000_000) * 3.0 + (500 / 1_000_000) * 15.0
        assert abs(cost - expected) < 1e-10

    def test_unknown_model_returns_zero(self):
        cost = calculate_cost("unknown/model", 1000, 500)
        assert cost == 0.0

    def test_zero_tokens(self):
        cost = calculate_cost("anthropic/claude-sonnet-4-20250514", 0, 0)
        assert cost == 0.0


# ============================================================
# track_usage
# ============================================================


class TestTrackUsage:
    @patch("data.llm.st.session_state", {})
    def test_first_call_initializes(self):
        from data.llm import track_usage

        track_usage("anthropic/claude-sonnet-4-20250514", 100, 50)
        from data.llm import st

        usage = st.session_state["llm_usage"]
        assert usage["total_tokens"] == 150
        assert usage["total_prompt_tokens"] == 100
        assert usage["total_completion_tokens"] == 50
        assert usage["request_count"] == 1
        assert usage["last_request_tokens"] == 150
        assert usage["total_cost_usd"] > 0

    @patch("data.llm.st.session_state", {})
    def test_accumulates(self):
        from data.llm import track_usage

        track_usage("anthropic/claude-sonnet-4-20250514", 100, 50)
        track_usage("anthropic/claude-sonnet-4-20250514", 200, 100)
        from data.llm import st

        usage = st.session_state["llm_usage"]
        assert usage["total_tokens"] == 450
        assert usage["total_prompt_tokens"] == 300
        assert usage["total_completion_tokens"] == 150
        assert usage["request_count"] == 2
        assert usage["last_request_tokens"] == 300


# ============================================================
# stream_chat_response captures usage
# ============================================================


class TestStreamCapturesUsage:
    @patch("data.llm.st.session_state", {})
    @patch("data.llm.get_openrouter_client")
    def test_captures_usage_from_last_chunk(self, mock_get_client):
        # Build mock chunks: text chunk + final usage chunk
        text_chunk = MagicMock()
        text_chunk.choices = [MagicMock()]
        text_chunk.choices[0].delta.content = "Hello"
        text_chunk.usage = None

        usage_chunk = MagicMock()
        usage_chunk.choices = []
        usage_chunk.usage = MagicMock()
        usage_chunk.usage.prompt_tokens = 50
        usage_chunk.usage.completion_tokens = 20

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = iter([text_chunk, usage_chunk])
        mock_get_client.return_value = mock_client

        from data.llm import stream_chat_response

        messages = [{"role": "user", "content": "Hi"}]
        model_key = "Claude Sonnet 4.6 (~$2.25/sess\u00e3o)"
        chunks = list(stream_chat_response(messages, model_key))
        assert "Hello" in chunks

        from data.llm import st

        usage = st.session_state.get("llm_usage", {})
        assert usage["total_tokens"] == 70
        assert usage["request_count"] == 1


# ============================================================
# call_chat_response captures usage
# ============================================================


class TestCallCapturesUsage:
    @patch("data.llm.st.session_state", {})
    @patch("data.llm.get_openrouter_client")
    def test_captures_usage(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 80
        mock_response.usage.completion_tokens = 40
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from data.llm import call_chat_response

        result = call_chat_response(
            [{"role": "user", "content": "Hi"}],
            "Claude Sonnet 4.6 (~$2.25/sess\u00e3o)",
        )
        assert result == "Resposta"

        from data.llm import st

        usage = st.session_state.get("llm_usage", {})
        assert usage["total_tokens"] == 120
        assert usage["request_count"] == 1


# ============================================================
# calculate_cost — Perplexity models
# ============================================================


class TestCalculateCostPerplexity:
    def test_sonar_cost(self):
        # Sonar: input=1.0/1M, output=1.0/1M
        cost = calculate_cost("perplexity/sonar", 10000, 5000)
        expected = (10000 / 1_000_000) * 1.0 + (5000 / 1_000_000) * 1.0
        assert abs(cost - expected) < 1e-10

    def test_sonar_pro_cost(self):
        # Sonar Pro: input=3.0/1M, output=15.0/1M
        cost = calculate_cost("perplexity/sonar-pro", 10000, 5000)
        expected = (10000 / 1_000_000) * 3.0 + (5000 / 1_000_000) * 15.0
        assert abs(cost - expected) < 1e-10

    def test_sonar_deep_research_cost(self):
        # Sonar Deep Research: input=2.0/1M, output=8.0/1M
        cost = calculate_cost("perplexity/sonar-deep-research", 10000, 5000)
        expected = (10000 / 1_000_000) * 2.0 + (5000 / 1_000_000) * 8.0
        assert abs(cost - expected) < 1e-10


# ============================================================
# _track_usage_from_response
# ============================================================


class TestTrackUsageFromResponse:
    @patch("data.llm.st.session_state", {})
    def test_tracks_from_response_with_usage(self):
        response = MagicMock()
        response.usage.prompt_tokens = 100
        response.usage.completion_tokens = 50
        _track_usage_from_response("anthropic/claude-sonnet-4-20250514", response)

        from data.llm import st

        usage = st.session_state.get("llm_usage", {})
        assert usage["total_tokens"] == 150
        assert usage["request_count"] == 1

    @patch("data.llm.st.session_state", {})
    def test_skips_when_no_usage(self):
        response = MagicMock()
        response.usage = None
        _track_usage_from_response("anthropic/claude-sonnet-4-20250514", response)

        from data.llm import st

        assert "llm_usage" not in st.session_state


# ============================================================
# stream_chat_response_with_tools
# ============================================================


class TestStreamWithTools:
    @patch("data.llm.st.session_state", {})
    @patch("data.llm.get_openrouter_client")
    def test_no_tool_calls_returns_text(self, mock_get_client):
        """When model doesn't call any tool, yield text directly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.content = "Aqui esta a resposta"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 30

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from data.llm import stream_chat_response_with_tools

        executor = MagicMock(return_value="search results")
        chunks = list(
            stream_chat_response_with_tools(
                [{"role": "user", "content": "Ola"}],
                "Claude Sonnet 4.6 (~$2.25/sess\u00e3o)",
                [{"type": "function", "function": {"name": "web_search"}}],
                executor,
            )
        )
        assert "Aqui esta a resposta" in chunks
        executor.assert_not_called()

    @patch("data.llm.st.session_state", {})
    @patch("data.llm.get_openrouter_client")
    def test_with_tool_call(self, mock_get_client):
        """When model calls a tool, execute it and return final answer."""
        # First call: model requests tool
        tool_call = MagicMock()
        tool_call.id = "call_123"
        tool_call.function.name = "web_search"
        tool_call.function.arguments = '{"query": "SUZB3 news"}'

        first_response = MagicMock()
        first_response.choices = [MagicMock()]
        first_response.choices[0].finish_reason = "tool_calls"
        first_response.choices[0].message.content = ""
        first_response.choices[0].message.tool_calls = [tool_call]
        first_response.usage = MagicMock()
        first_response.usage.prompt_tokens = 100
        first_response.usage.completion_tokens = 20

        # Second call: model returns final text
        second_response = MagicMock()
        second_response.choices = [MagicMock()]
        second_response.choices[0].finish_reason = "stop"
        second_response.choices[0].message.content = "SUZB3 subiu 5%"
        second_response.choices[0].message.tool_calls = None
        second_response.usage = MagicMock()
        second_response.usage.prompt_tokens = 200
        second_response.usage.completion_tokens = 40

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [first_response, second_response]
        mock_get_client.return_value = mock_client

        from data.llm import stream_chat_response_with_tools

        executor = MagicMock(return_value="Search result: SUZB3 up 5%")
        chunks = list(
            stream_chat_response_with_tools(
                [{"role": "user", "content": "Noticias SUZB3"}],
                "Claude Sonnet 4.6 (~$2.25/sess\u00e3o)",
                [{"type": "function", "function": {"name": "web_search"}}],
                executor,
            )
        )

        # Should have status message and final text
        full_text = "".join(chunks)
        assert "Buscando: SUZB3 news" in full_text
        assert "SUZB3 subiu 5%" in full_text
        executor.assert_called_once_with("web_search", {"query": "SUZB3 news"})

    @patch("data.llm.st.session_state", {})
    @patch("data.llm.get_openrouter_client")
    def test_tracks_usage_on_tool_rounds(self, mock_get_client):
        """Usage is tracked for each non-streaming round."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.content = "Done"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        from data.llm import stream_chat_response_with_tools

        list(
            stream_chat_response_with_tools(
                [{"role": "user", "content": "Hi"}],
                "Claude Sonnet 4.6 (~$2.25/sess\u00e3o)",
                [],
                MagicMock(),
            )
        )

        from data.llm import st

        usage = st.session_state.get("llm_usage", {})
        assert usage["total_tokens"] == 150
        assert usage["request_count"] == 1

    @patch("data.llm.st.session_state", {})
    @patch("data.llm.get_openrouter_client", side_effect=Exception("API down"))
    def test_api_error(self, mock_get_client):
        """API errors are yielded as error messages."""
        from data.llm import stream_chat_response_with_tools

        chunks = list(
            stream_chat_response_with_tools(
                [{"role": "user", "content": "Hi"}],
                "Claude Sonnet 4.6 (~$2.25/sess\u00e3o)",
                [],
                MagicMock(),
            )
        )
        assert any("Erro na API" in c for c in chunks)
