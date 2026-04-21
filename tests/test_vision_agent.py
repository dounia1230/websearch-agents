from __future__ import annotations

from pathlib import Path

from app.agents.vision_agent import run_vision
from app.config import AppConfig
from app.state import make_initial_state


def _config() -> AppConfig:
    return AppConfig(
        llm_provider="ollama",
        text_model="qwen3:8b",
        vision_model="llama3.2-vision:latest",
        embedding_model="nomic-embed-text:latest",
        ollama_base_url="http://localhost:11434",
        openai_api_key="",
        openai_base_url="",
        anthropic_api_key="",
        groq_api_key="",
        tavily_api_key="test",
        max_search_results=5,
        max_reader_results=2,
        max_research_passes=2,
        max_follow_up_queries=2,
        max_generation_tokens=400,
        max_source_content_chars=2000,
        max_reader_content_chars=4000,
        request_timeout_seconds=20,
        tavily_search_depth="advanced",
        tavily_topic="general",
        min_source_quality_score=0.55,
        retrieval_top_k=3,
        private_data_dir=None,
        chroma_persist_dir=None,
        chroma_collection_name="test",
    )


def test_run_vision_records_issue_when_image_is_missing() -> None:
    missing_path = str(Path("missing-image.png").resolve())
    state = make_initial_state("What is in this image?", image_paths=[missing_path])

    result = run_vision(state, _config())

    assert result["vision"].confidence == 0.0
    assert result["errors"][0].stage == "vision"
    assert "missing-image.png" in result["errors"][0].message
