from __future__ import annotations

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.critic_prompt import CRITIC_SYSTEM_PROMPT
from app.schemas import CritiqueReport, SourceAssessment, SourceRecord
from app.state import ResearchState, serialize_issues_for_prompt, serialize_sources_for_prompt
from app.utils.source_quality import apply_source_assessment


def run_critic(state: ResearchState, config: AppConfig) -> ResearchState:
    research_brief = state.get("research_brief")
    query_plan = state.get("query_plan")
    selected_sources = state.get("selected_sources", [])
    if research_brief is None:
        raise RuntimeError("Critic agent requires a research brief.")
    if query_plan is None:
        raise RuntimeError("Critic agent requires a planner output.")

    critique = invoke_structured_model(
        config=config,
        schema=CritiqueReport,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        user_input="\n\n".join(
            [
                f"Question:\n{state['question']}",
                f"Interpreted query plan:\n{query_plan.model_dump_json(indent=2)}",
                f"Research pass count:\n{state.get('research_passes', 0)} of {config.max_research_passes}",
                f"Selected sources:\n{serialize_sources_for_prompt(selected_sources)}",
                f"Research brief:\n{research_brief.model_dump_json(indent=2)}",
                f"Known pipeline issues:\n{serialize_issues_for_prompt(state.get('errors', []))}",
            ]
        ),
    )

    filtered_sources = _filter_sources_with_critique(
        sources=selected_sources,
        assessments=critique.source_assessments,
        config=config,
    )
    if selected_sources and not filtered_sources:
        critique = critique.model_copy(
            update={
                "needs_revision": True,
                "rationale": f"{critique.rationale} All currently selected sources were rejected as off-intent or too broad.",
            }
        )

    return {
        "critique": critique,
        "selected_sources": filtered_sources,
    }


def _filter_sources_with_critique(
    *,
    sources: list[SourceRecord],
    assessments: list[SourceAssessment],
    config: AppConfig,
) -> list[SourceRecord]:
    assessment_lookup = {assessment.source_id: assessment for assessment in assessments}
    filtered_sources: list[SourceRecord] = []

    for source in sources:
        assessment = assessment_lookup.get(source.id)
        if assessment is None:
            filtered_sources.append(source)
            continue

        reviewed_source = apply_source_assessment(
            source,
            assessment,
            minimum_relevance_score=config.min_critic_relevance_score,
            minimum_overall_score=config.min_critic_overall_score,
        )
        if reviewed_source.included:
            filtered_sources.append(reviewed_source)

    filtered_sources.sort(
        key=lambda source: (
            source.relevance_to_user_intent_score
            or source.intent_alignment_score
            or 0.0,
            source.critic_score or source.quality_score or 0.0,
        ),
        reverse=True,
    )
    return filtered_sources
