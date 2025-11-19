from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from .config import get_settings

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    """Lazily create a shared AsyncOpenAI client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def call_llm(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: int | None = 1024,
) -> str:
    """Unified chat-style LLM call helper that returns plain text."""
    settings = get_settings()
    client = get_client()
    model_name = model or settings.openai_model

    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_output_tokens,
    )

    choice = response.choices[0]
    return choice.message.content or ""


