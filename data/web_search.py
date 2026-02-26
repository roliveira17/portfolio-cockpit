"""Busca web via Tavily API para o Chat Assessor."""

import logging

import streamlit as st

logger = logging.getLogger(__name__)

# OpenAI-compatible tool definition for web_search
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for recent information about stocks, market news, earnings, "
            "economic data, or any topic the user asks about. Use when the user asks about "
            "recent events, news, releases, or data not available in the conversation context."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and include ticker symbols when relevant.",
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "description": "Use 'basic' for quick factual queries, 'advanced' for in-depth research.",
                },
                "topic": {
                    "type": "string",
                    "enum": ["general", "news", "finance"],
                    "description": "Use 'finance' for stocks/market, 'news' for current events.",
                },
            },
            "required": ["query"],
        },
    },
}

MAX_RESULT_CHARS = 4000


def is_search_available() -> bool:
    """Check if Tavily API key is configured in secrets."""
    try:
        key = st.secrets.get("tavily", {}).get("api_key", "")
        return bool(key)
    except Exception:
        return False


def _get_tavily_api_key() -> str:
    """Return Tavily API key from secrets."""
    return st.secrets["tavily"]["api_key"]


def execute_web_search(
    query: str,
    search_depth: str = "basic",
    topic: str = "general",
    max_results: int = 5,
) -> str:
    """Execute web search via Tavily and return formatted results string."""
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=_get_tavily_api_key())
        response = client.search(
            query=query,
            search_depth=search_depth,
            topic=topic,
            max_results=max_results,
        )
        return _format_search_results(response)
    except ImportError:
        logger.warning("tavily-python not installed")
        return "Erro: biblioteca tavily-python nao instalada."
    except Exception as e:
        logger.warning(f"Tavily search error: {e}")
        return f"Erro na busca web: {e}"


def _format_search_results(response: dict) -> str:
    """Format Tavily response into a readable string for the LLM."""
    results = response.get("results", [])
    if not results:
        return "Nenhum resultado encontrado."

    parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "Sem titulo")
        url = r.get("url", "")
        content = r.get("content", "")
        parts.append(f"[{i}] {title}\n{url}\n{content}")

    output = "\n\n".join(parts)
    if len(output) > MAX_RESULT_CHARS:
        output = output[:MAX_RESULT_CHARS] + "\n\n[... resultados truncados ...]"
    return output
