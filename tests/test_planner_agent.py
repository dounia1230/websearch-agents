from __future__ import annotations

from unittest.mock import patch

from app.agents.planner_agent import run_planner
from app.config import AppConfig
from app.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from app.schemas import PlannerOutput
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
        min_intent_alignment_score=0.3,
        min_critic_relevance_score=0.55,
        min_critic_overall_score=0.6,
        retrieval_top_k=3,
        private_data_dir=None,
        chroma_persist_dir=None,
        chroma_collection_name="test",
    )


def test_run_planner_returns_structured_query_plan() -> None:
    expected_plan = PlannerOutput(
        interpreted_query="Find specific AI companies in Morocco.",
        user_intent="The user wants company examples, not broad AI policy coverage.",
        search_queries=[
            "top AI companies Morocco",
            "AI startups Morocco",
            "leading artificial intelligence companies Morocco",
        ],
        include_topics=["company", "startup", "Morocco"],
        exclude_topics=["policy", "economy", "macro"],
        notes="Prioritize entity-level company results.",
    )

    with patch("app.agents.planner_agent.invoke_structured_model", return_value=expected_plan):
        result = run_planner(make_initial_state("i mean the ai company in morocco"), _config())

    assert result["query_plan"] == expected_plan
    assert len(result["search_queries"]) == 3
    assert result["query_plan"].exclude_topics == ["policy", "economy", "macro"]


def test_planner_prompt_matches_output_schema() -> None:
    for field_name in PlannerOutput.model_fields:
        assert f'"{field_name}"' in PLANNER_SYSTEM_PROMPT

    assert "3 to 5 precise web search queries" in PLANNER_SYSTEM_PROMPT
