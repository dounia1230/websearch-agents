from __future__ import annotations

from unittest.mock import patch

from app.agents.critic_agent import run_critic
from app.config import AppConfig
from app.schemas import CritiqueReport, PlannerOutput, ResearchBrief, SourceAssessment, SourceRecord
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


def test_run_critic_filters_broad_but_high_quality_sources() -> None:
    specific_source = SourceRecord(
        id="S1",
        title="Leading AI Companies in Morocco",
        url="https://example.com/ai-companies-morocco",
        snippet="Specific company list.",
        raw_content="x" * 1000,
        extracted_content="",
        source_type="web",
        search_score=0.9,
        quality_score=0.9,
        intent_alignment_score=0.85,
    )
    broad_source = SourceRecord(
        id="S2",
        title="National AI Policy Outlook",
        url="https://example.com/ai-policy-outlook",
        snippet="Broad policy overview.",
        raw_content="x" * 1200,
        extracted_content="",
        source_type="web",
        search_score=0.92,
        quality_score=0.95,
        intent_alignment_score=0.35,
    )

    critique = CritiqueReport(
        needs_revision=False,
        rationale="One source is off-intent and should be removed.",
        missing_angles=[],
        unsupported_or_weak_claims=[],
        follow_up_queries=[],
        source_assessments=[
            SourceAssessment(
                source_id="S1",
                authority=0.9,
                relevance_to_user_intent=0.92,
                specificity=0.88,
                recency=0.74,
                evidence=0.8,
                clarity=0.82,
                include=True,
                rationale="Directly answers the company-focused question.",
            ),
            SourceAssessment(
                source_id="S2",
                authority=0.94,
                relevance_to_user_intent=0.22,
                specificity=0.28,
                recency=0.7,
                evidence=0.76,
                clarity=0.84,
                include=False,
                rationale="High quality but wrong context for a company-specific question.",
            ),
        ],
        confidence=0.84,
    )

    with patch("app.agents.critic_agent.invoke_structured_model", return_value=critique):
        state = make_initial_state("i mean the ai company")
        state["query_plan"] = PlannerOutput(
            interpreted_query="Find specific AI companies, not policy overviews.",
            user_intent="The user wants concrete company examples.",
            search_queries=[
                "top ai companies",
                "ai startup examples",
                "leading artificial intelligence companies",
            ],
            include_topics=["company", "startup"],
            exclude_topics=["policy", "economy", "macro"],
            notes="Entity-level results only.",
        )
        state["research_brief"] = ResearchBrief(
            query_scope="company-focused AI landscape",
            key_findings=["Specific companies were identified [S1]."],
            source_assessment=["S2 is broader than needed."],
            open_questions=[],
            recommended_follow_up=[],
            confidence=0.8,
        )
        state["selected_sources"] = [specific_source, broad_source]
        result = run_critic(state, _config())

    assert [source.id for source in result["selected_sources"]] == ["S1"]
    assert result["selected_sources"][0].critic_score is not None
    assert result["selected_sources"][0].relevance_to_user_intent_score == 0.92
