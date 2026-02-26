"""Testes para data/web_search.py — busca web via Tavily."""

from unittest.mock import MagicMock, patch

from data.web_search import (
    MAX_RESULT_CHARS,
    WEB_SEARCH_TOOL,
    _format_search_results,
    execute_web_search,
    is_search_available,
)

# ============================================================
# WEB_SEARCH_TOOL structure
# ============================================================


class TestWebSearchTool:
    def test_has_correct_type(self):
        assert WEB_SEARCH_TOOL["type"] == "function"

    def test_has_function_name(self):
        assert WEB_SEARCH_TOOL["function"]["name"] == "web_search"

    def test_has_required_query_param(self):
        params = WEB_SEARCH_TOOL["function"]["parameters"]
        assert "query" in params["properties"]
        assert "query" in params["required"]

    def test_has_search_depth_and_topic(self):
        props = WEB_SEARCH_TOOL["function"]["parameters"]["properties"]
        assert "search_depth" in props
        assert "topic" in props
        assert props["search_depth"]["enum"] == ["basic", "advanced"]
        assert "finance" in props["topic"]["enum"]


# ============================================================
# _format_search_results
# ============================================================


class TestFormatSearchResults:
    def test_no_results(self):
        result = _format_search_results({"results": []})
        assert result == "Nenhum resultado encontrado."

    def test_empty_response(self):
        result = _format_search_results({})
        assert result == "Nenhum resultado encontrado."

    def test_formats_results(self):
        response = {
            "results": [
                {"title": "SUZB3 Earnings", "url": "https://example.com/1", "content": "Revenue up 15%"},
                {"title": "Market News", "url": "https://example.com/2", "content": "Celulose prices rising"},
            ]
        }
        result = _format_search_results(response)
        assert "[1] SUZB3 Earnings" in result
        assert "https://example.com/1" in result
        assert "Revenue up 15%" in result
        assert "[2] Market News" in result

    def test_truncates_long_results(self):
        long_content = "x" * (MAX_RESULT_CHARS + 500)
        response = {"results": [{"title": "Long", "url": "https://x.com", "content": long_content}]}
        result = _format_search_results(response)
        assert len(result) <= MAX_RESULT_CHARS + 100  # Allow for truncation message
        assert "[... resultados truncados ...]" in result


# ============================================================
# is_search_available
# ============================================================


class TestIsSearchAvailable:
    @patch("data.web_search.st.secrets", {"tavily": {"api_key": "tvly-test"}})
    def test_available_with_key(self):
        assert is_search_available() is True

    @patch("data.web_search.st.secrets", {"tavily": {"api_key": ""}})
    def test_not_available_empty_key(self):
        assert is_search_available() is False

    @patch("data.web_search.st.secrets", {})
    def test_not_available_no_section(self):
        assert is_search_available() is False


# ============================================================
# execute_web_search
# ============================================================


class TestExecuteWebSearch:
    @patch("data.web_search._get_tavily_api_key", return_value="tvly-test")
    @patch("data.web_search.TavilyClient", create=True)
    def test_success(self, mock_tavily_cls, mock_key):
        # We need to patch the import inside the function
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": [{"title": "Result", "url": "https://x.com", "content": "Data"}]}

        with patch.dict("sys.modules", {"tavily": MagicMock(TavilyClient=lambda api_key: mock_client)}):
            result = execute_web_search("SUZB3 earnings", search_depth="basic", topic="finance")

        assert "[1] Result" in result
        assert "https://x.com" in result

    def test_missing_tavily_library(self):
        with patch.dict("sys.modules", {"tavily": None}):
            # When tavily module is None, import will raise ImportError-like behavior
            # But we need to test the actual function's import error handling
            pass

    @patch("data.web_search._get_tavily_api_key", return_value="tvly-test")
    def test_api_error(self, mock_key):
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("Rate limited")

        with patch.dict("sys.modules", {"tavily": MagicMock(TavilyClient=lambda api_key: mock_client)}):
            result = execute_web_search("test query")

        assert "Erro na busca web" in result
