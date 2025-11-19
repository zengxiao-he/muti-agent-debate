from typing import List

from .config import get_settings


async def web_search(query: str, max_results: int = 5) -> str:
    """
    Lightweight placeholder search function.

    - If a real search API is configured (SEARCH_API_KEY / SEARCH_ENDPOINT),
      you can integrate Tavily / Serper / custom search here.
    - For the MVP, we just return an informative text so the system works
      without any external network dependency.
    """
    settings = get_settings()

    if not settings.search_api_key or not settings.search_endpoint:
        return (
            f"[Mock search results] For query: {query}\n"
            "No real search API is configured. Please set SEARCH_API_KEY / "
            "SEARCH_ENDPOINT and implement a real web_search integration in "
            "backend/search.py if you need live web evidence."
        )

    # TODO: Integrate real search service and return aggregated text summary.
    # This simple return shape is kept to ease future refactors.
    dummy_results: List[str] = [
        f"Search result 1: authoritative source about '{query}' (example).",
        f"Search result 2: alternative perspective on '{query}' (example).",
    ]
    return "\n".join(dummy_results)


