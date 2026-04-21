from __future__ import annotations

import json
import logging

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.research_prompt import RESEARCH_SYSTEM_PROMPT
from app.schemas import PipelineIssue, ResearchBrief, SourceRecord
from app.state import ResearchState, append_issues, serialize_issues_for_prompt, serialize_sources_for_prompt
from app.tools.jina_reader import read_url
from app.tools.private_retrieval import retrieve_private_context
from app.tools.tavily_tool import search_web
from app.utils.source_quality import deduplicate_sources, evaluate_source_quality, merge_sources

logger = logging.getLogger(__name__)


def run_research(state: ResearchState, config: AppConfig) -> ResearchState:
    question = state["question"].strip()
    research_pass = state.get("research_passes", 0) + 1
    prior_critique = state.get("critique")
    critique_queries = prior_critique.follow_up_queries if prior_critique else []
    search_queries = _build_search_queries(question, critique_queries, config.max_follow_up_queries)
    issues: list[PipelineIssue] = []

    private_sources, retrieval_issues = retrieve_private_context(question, config)
    issues.extend(retrieval_issues)

    new_web_sources: list[SourceRecord] = []
    for query in search_queries:
        try:
            new_web_sources.extend(search_web(query, config))
        except Exception as exc:
            logger.exception("Search failed for query %s", query)
            issues.append(
                PipelineIssue(
                    stage="research",
                    message=f"Search failed for query '{query}': {exc}",
                    recoverable=True,
                    details={"query": query},
                )
            )

    enriched_web_sources, extraction_issues = _enrich_web_sources(new_web_sources, config)
    issues.extend(extraction_issues)

    all_candidates = merge_sources(
        state.get("candidate_sources", []),
        deduplicate_sources([*enriched_web_sources, *private_sources]),
    )
    all_candidates = _reindex_sources(all_candidates)

    selected_sources = [
        evaluate_source_quality(source, config.min_source_quality_score)
        for source in all_candidates
    ]
    selected_sources = [source for source in selected_sources if source.included]
    selected_sources.sort(key=lambda source: source.quality_score or 0.0, reverse=True)

    if not selected_sources:
        raise RuntimeError("No usable sources were collected from Tavily or private retrieval.")

    brief = invoke_structured_model(
        config=config,
        schema=ResearchBrief,
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        user_input=_build_research_prompt_input(
            question=question,
            research_pass=research_pass,
            critique=prior_critique.model_dump() if prior_critique else None,
            sources=selected_sources,
            issues=issues,
        ),
    )

    return {
        "research_passes": research_pass,
        "search_queries": search_queries,
        "candidate_sources": all_candidates,
        "selected_sources": selected_sources,
        "research_brief": brief,
        "errors": append_issues(state.get("errors", []), issues),
    }


def _build_search_queries(question: str, follow_up_queries: list[str], limit: int) -> list[str]:
    queries = [question]
    for query in follow_up_queries[:limit]:
        normalized = query.strip()
        if normalized and normalized not in queries:
            queries.append(normalized)
    return queries


def _build_research_prompt_input(
    *,
    question: str,
    research_pass: int,
    critique: dict | None,
    sources: list[SourceRecord],
    issues: list[PipelineIssue],
) -> str:
    return "\n\n".join(
        [
            f"Question:\n{question}",
            f"Research pass:\n{research_pass}",
            "Prior critique:\n" + ("null" if critique is None else json.dumps(critique, indent=2)),
            f"Structured sources:\n{serialize_sources_for_prompt(sources)}",
            f"Known pipeline issues:\n{serialize_issues_for_prompt(issues)}",
        ]
    )


def _enrich_web_sources(
    sources: list[SourceRecord],
    config: AppConfig,
) -> tuple[list[SourceRecord], list[PipelineIssue]]:
    issues: list[PipelineIssue] = []
    enriched_sources: list[SourceRecord] = []

    for index, source in enumerate(deduplicate_sources(sources)):
        enriched_source = source.model_copy()
        enriched_source = enriched_source.model_copy(
            update={"raw_content": _truncate(enriched_source.raw_content, config.max_source_content_chars)}
        )

        if index < config.max_reader_results and enriched_source.url:
            try:
                extracted_content = read_url(
                    enriched_source.url,
                    timeout_seconds=config.request_timeout_seconds,
                )
                enriched_source = enriched_source.model_copy(
                    update={
                        "extracted_content": _truncate(extracted_content, config.max_reader_content_chars),
                        "extraction_status": "success",
                        "extraction_error": None,
                    }
                )
            except Exception as exc:
                logger.exception("Content extraction failed for %s", enriched_source.url)
                enriched_source = enriched_source.model_copy(
                    update={
                        "extracted_content": "",
                        "extraction_status": "failed",
                        "extraction_error": str(exc),
                    }
                )
                issues.append(
                    PipelineIssue(
                        stage="research",
                        message=f"Content extraction failed for {enriched_source.url}: {exc}",
                        recoverable=True,
                        details={"source_id": enriched_source.id, "url": enriched_source.url},
                    )
                )

        enriched_sources.append(enriched_source)

    return enriched_sources, issues


def _reindex_sources(sources: list[SourceRecord]) -> list[SourceRecord]:
    web_counter = 0
    private_counter = 0
    reindexed: list[SourceRecord] = []
    for source in sources:
        if source.source_type == "private_data":
            private_counter += 1
            new_id = f"P{private_counter}"
        else:
            web_counter += 1
            new_id = f"S{web_counter}"
        reindexed.append(source.model_copy(update={"id": new_id}))
    return reindexed


def _truncate(text: str, limit: int) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[:limit].rstrip()}..."
