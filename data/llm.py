"""Cliente OpenRouter para chat do Assessor de Investimentos."""

import base64
import json
import logging
from collections.abc import Generator

import streamlit as st
from openai import OpenAI

from utils.constants import OPENROUTER_MODELS

logger = logging.getLogger(__name__)


def get_openrouter_client() -> OpenAI:
    """Return OpenRouter client (OpenAI-compatible)."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["openrouter"]["api_key"],
    )


def stream_chat_response(messages: list[dict], model_key: str) -> Generator[str, None, None]:
    """Stream chat response from OpenRouter. Yields text chunks."""
    model_id = OPENROUTER_MODELS[model_key]["id"]
    try:
        client = get_openrouter_client()
        stream = client.chat.completions.create(
            model=model_id,
            messages=messages,
            stream=True,
            max_tokens=4096,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.warning(f"OpenRouter stream error: {e}")
        yield f"\n\n**Erro na API:** {e}"


def call_chat_response(messages: list[dict], model_key: str) -> str:
    """Non-streaming call for structured extraction (JSON parsing)."""
    model_id = OPENROUTER_MODELS[model_key]["id"]
    try:
        client = get_openrouter_client()
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.warning(f"OpenRouter call error: {e}")
        return ""


def encode_image_to_base64(uploaded_file) -> str:
    """Encode a Streamlit UploadedFile to base64 string."""
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def build_vision_content(text: str, image_base64: str, mime_type: str) -> list[dict]:
    """Build OpenAI multipart content with text + image."""
    return [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}},
    ]


def extract_structured_data(messages: list[dict], model_key: str, extraction_prompt: str) -> dict | None:
    """Extract structured JSON from conversation using a specialized prompt."""
    extraction_messages = [
        {"role": "system", "content": extraction_prompt},
        {"role": "user", "content": _summarize_conversation(messages)},
    ]
    raw = call_chat_response(extraction_messages, model_key)
    return _parse_json_from_response(raw)


def _summarize_conversation(messages: list[dict]) -> str:
    """Flatten conversation into a single string for extraction."""
    parts = []
    for msg in messages:
        role = "Usuário" if msg["role"] == "user" else "Assessor"
        content = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


def _parse_json_from_response(text: str) -> dict | None:
    """Extract JSON object from LLM response text."""
    if not text:
        return None
    # Try to find JSON block in markdown code fence
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        text = text[start:end].strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Falha ao parsear JSON da resposta LLM")
        return None
