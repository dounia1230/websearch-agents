from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return int(raw_value)


def _read_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return float(raw_value)


def _read_path(name: str) -> Path | None:
    raw_value = os.getenv(name, "").strip()
    return Path(raw_value).expanduser().resolve() if raw_value else None


def _normalize_ollama_base_url(raw_value: str) -> str:
    cleaned = raw_value.strip().rstrip("/")
    if cleaned.endswith("/api"):
        cleaned = cleaned[: -len("/api")]
    return cleaned or "http://localhost:11434"


@dataclass(frozen=True)
class AppConfig:
    llm_provider: str
    text_model: str
    vision_model: str
    embedding_model: str
    ollama_base_url: str
    openai_api_key: str
    openai_base_url: str
    anthropic_api_key: str
    groq_api_key: str
    tavily_api_key: str
    max_search_results: int
    max_reader_results: int
    max_research_passes: int
    max_follow_up_queries: int
    max_generation_tokens: int
    max_source_content_chars: int
    max_reader_content_chars: int
    request_timeout_seconds: int
    tavily_search_depth: str
    tavily_topic: str
    min_source_quality_score: float
    retrieval_top_k: int
    private_data_dir: Path | None
    chroma_persist_dir: Path | None
    chroma_collection_name: str


def load_config() -> AppConfig:
    ollama_base_url = _normalize_ollama_base_url(os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    private_data_dir = _read_path("PRIVATE_DATA_DIR")
    chroma_persist_dir = _read_path("CHROMA_PERSIST_DIR")

    return AppConfig(
        llm_provider=os.getenv("LLM_PROVIDER", "ollama").strip().lower() or "ollama",
        text_model=os.getenv("TEXT_MODEL", "qwen3:8b").strip() or "qwen3:8b",
        vision_model=os.getenv("VISION_MODEL", "llama3.2-vision:latest").strip()
        or "llama3.2-vision:latest",
        embedding_model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest").strip()
        or "nomic-embed-text:latest",
        ollama_base_url=ollama_base_url,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", "").strip(),
        groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
        tavily_api_key=os.getenv("TAVILY_API_KEY", "").strip(),
        max_search_results=_read_int("MAX_SEARCH_RESULTS", 6),
        max_reader_results=_read_int("MAX_READER_RESULTS", 4),
        max_research_passes=_read_int("MAX_RESEARCH_PASSES", 2),
        max_follow_up_queries=_read_int("MAX_FOLLOW_UP_QUERIES", 2),
        max_generation_tokens=_read_int("MAX_GENERATION_TOKENS", 1200),
        max_source_content_chars=_read_int("MAX_SOURCE_CONTENT_CHARS", 2500),
        max_reader_content_chars=_read_int("MAX_READER_CONTENT_CHARS", 4500),
        request_timeout_seconds=_read_int("REQUEST_TIMEOUT_SECONDS", 30),
        tavily_search_depth=os.getenv("TAVILY_SEARCH_DEPTH", "advanced").strip() or "advanced",
        tavily_topic=os.getenv("TAVILY_TOPIC", "general").strip() or "general",
        min_source_quality_score=_read_float("MIN_SOURCE_QUALITY_SCORE", 0.55),
        retrieval_top_k=_read_int("RETRIEVAL_TOP_K", 3),
        private_data_dir=private_data_dir,
        chroma_persist_dir=chroma_persist_dir,
        chroma_collection_name=os.getenv("CHROMA_COLLECTION_NAME", "research_assistant").strip()
        or "research_assistant",
    )
