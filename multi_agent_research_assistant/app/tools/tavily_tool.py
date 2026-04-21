from __future__ import annotations

from typing import Any

from app.config import AppConfig
from app.schemas import SourceRecord


def search_web(query: str, config: AppConfig) -> list[SourceRecord]:
    from tavily import TavilyClient

    if not config.tavily_api_key:
        raise ValueError("TAVILY_API_KEY is required for Tavily search.")

    client = TavilyClient(api_key=config.tavily_api_key)
    payload = client.search(
        query=query,
        search_depth=config.tavily_search_depth,
        max_results=config.max_search_results,
        include_answer=False,
        include_raw_content=True,
        topic=config.tavily_topic,
    )

    results: list[dict[str, Any]]
    if isinstance(payload, list):
        results = payload
    else:
        results = list(payload.get("results", []))

    normalized: list[SourceRecord] = []
    for index, result in enumerate(results, start=1):
        normalized.append(
            SourceRecord(
                id=f"S{index}",
                title=str(result.get("title") or f"Source {index}"),
                url=str(result.get("url") or ""),
                snippet=str(result.get("content") or "").strip(),
                raw_content=str(result.get("raw_content") or "").strip(),
                extracted_content="",
                source_type="web",
                search_score=_coerce_score(result.get("score")),
                metadata={"query": query},
            )
        )

    return normalized


def _coerce_score(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
