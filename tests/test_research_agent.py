from __future__ import annotations

from unittest.mock import patch

from app.agents.research_agent import run_research
from app.config import AppConfig
from app.schemas import PlannerOutput, ResearchBrief, SourceRecord
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


def test_run_research_filters_low_quality_sources() -> None:
    good_source = SourceRecord(
        id="S1",
        title="CDC Guidance",
        url="https://www.cdc.gov/topic/report",
        snippet="Official guidance with detailed summary.",
        raw_content="x" * 1200,
        extracted_content="",
        source_type="web",
        search_score=0.9,
    )
    bad_source = SourceRecord(
        id="S2",
        title="Best cheap affiliate report",
        url="https://best-deals-affiliate.example.com/top-10-report",
        snippet="Tiny pitch.",
        raw_content="short",
        extracted_content="",
        source_type="web",
        search_score=0.1,
    )

    with (
        patch("app.agents.research_agent.retrieve_private_context", return_value=([], [])),
        patch("app.agents.research_agent.search_web", return_value=[good_source, bad_source]),
        patch("app.agents.research_agent.read_url", return_value="x" * 2000),
        patch(
            "app.agents.research_agent.invoke_structured_model",
            return_value=ResearchBrief(
                query_scope="public-health guidance",
                key_findings=["Finding [S1]"],
                source_assessment=["Reliable source coverage [S1]"],
                open_questions=[],
                recommended_follow_up=[],
                confidence=0.8,
            ),
        ),
    ):
        state = make_initial_state("What changed?")
        state["query_plan"] = PlannerOutput(
            interpreted_query="public-health guidance update",
            user_intent="Find specific guidance updates instead of general public health policy.",
            search_queries=[
                "public health guidance update",
                "cdc updated guidance report",
                "official public health advisory changes",
            ],
            include_topics=["guidance", "advisory", "cdc"],
            exclude_topics=["affiliate", "coupon", "deals"],
            notes="Prioritize official guidance pages.",
        )
        result = run_research(state, _config())

    assert len(result["candidate_sources"]) == 2
    assert [source.id for source in result["selected_sources"]] == ["S1"]
    assert result["selected_sources"][0].quality_label in {"high", "medium"}


def test_run_research_merges_results_from_multiple_planned_queries() -> None:
    common_source = SourceRecord(
        id="S1",
        title="OpenAI Startup Market Brief",
        url="https://example.com/startup-brief",
        snippet="Specific startup coverage.",
        raw_content="x" * 1000,
        extracted_content="",
        source_type="web",
        search_score=0.9,
    )
    extra_source = SourceRecord(
        id="S2",
        title="AI Company Ranking",
        url="https://example.com/company-ranking",
        snippet="Specific company ranking.",
        raw_content="x" * 1000,
        extracted_content="",
        source_type="web",
        search_score=0.8,
    )

    def search_side_effect(query: str, _config: AppConfig) -> list[SourceRecord]:
        if "startup" in query:
            return [common_source]
        if "company ranking" in query:
            return [common_source, extra_source]
        return []

    with (
        patch("app.agents.research_agent.retrieve_private_context", return_value=([], [])),
        patch("app.agents.research_agent.search_web", side_effect=search_side_effect) as mocked_search,
        patch("app.agents.research_agent.read_url", return_value="x" * 1500),
        patch(
            "app.agents.research_agent.invoke_structured_model",
            return_value=ResearchBrief(
                query_scope="ai company landscape",
                key_findings=["Finding [S1]"],
                source_assessment=["Specific company coverage [S1][S2]"],
                open_questions=[],
                recommended_follow_up=[],
                confidence=0.81,
            ),
        ),
    ):
        state = make_initial_state("i mean the ai company")
        state["query_plan"] = PlannerOutput(
            interpreted_query="Find specific AI companies and startups, not broad AI policy or macro economy context.",
            user_intent="The user wants concrete company examples.",
            search_queries=[
                "ai startup examples",
                "ai company ranking",
                "leading artificial intelligence companies",
            ],
            include_topics=["company", "startup"],
            exclude_topics=["policy", "economy", "macro"],
            notes="Entity-level company retrieval only.",
        )
        result = run_research(state, _config())

    assert mocked_search.call_count == 3
    assert len(result["candidate_sources"]) == 2
    assert {source.url for source in result["candidate_sources"]} == {
        "https://example.com/startup-brief",
        "https://example.com/company-ranking",
    }


def test_run_research_surfaces_tavily_dependency_errors() -> None:
    with (
        patch("app.agents.research_agent.retrieve_private_context", return_value=([], [])),
        patch(
            "app.agents.research_agent.search_web",
            side_effect=RuntimeError(
                "Tavily client dependency is missing. Install project requirements in the same Python environment."
            ),
        ),
    ):
        state = make_initial_state("What changed?")
        state["query_plan"] = PlannerOutput(
            interpreted_query="public-health guidance update",
            user_intent="Find specific guidance updates instead of general public health policy.",
            search_queries=[
                "public health guidance update",
                "cdc updated guidance report",
                "official public health advisory changes",
            ],
            include_topics=["guidance", "advisory", "cdc"],
            exclude_topics=["affiliate", "coupon", "deals"],
            notes="Prioritize official guidance pages.",
        )

        try:
            run_research(state, _config())
        except RuntimeError as exc:
            assert "Search failed for query" in str(exc)
            assert "Tavily client dependency is missing" in str(exc)
        else:
            raise AssertionError("Expected a Tavily dependency failure to be surfaced.")
