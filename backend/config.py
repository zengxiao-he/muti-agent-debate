import os
from functools import lru_cache


class Settings:
    """Global settings loaded from environment variables."""

    # Do NOT hardcode real API keys here. Use environment variables instead.
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    # Search related configuration (MVP can work without real search)
    search_api_key: str | None = None
    search_endpoint: str | None = None

    def __init__(self) -> None:
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.openai_model = os.environ.get("OPENAI_MODEL", self.openai_model)
        self.search_api_key = os.environ.get("SEARCH_API_KEY", None)
        self.search_endpoint = os.environ.get("SEARCH_ENDPOINT", None)


@lru_cache
def get_settings() -> Settings:
    return Settings()


