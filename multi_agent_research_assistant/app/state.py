from __future__ import annotations

import json
from typing import TypedDict

from app.schemas import (
    CritiqueReport,
    FinalReport,
    PipelineIssue,
    PlannerOutput,
    ResearchBrief,
    SourceRecord,
    SummaryReport,
    VisionReport,
)


class ResearchState(TypedDict, total=False):
    question: str
    image_paths: list[str]
    query_plan: PlannerOutput | None
    search_queries: list[str]
    research_passes: int
    candidate_sources: list[SourceRecord]
    selected_sources: list[SourceRecord]
    research_brief: ResearchBrief | None
    critique: CritiqueReport | None
    summary: SummaryReport | None
    vision: VisionReport | None
    final_report: FinalReport | None
    final_answer: str
    errors: list[PipelineIssue]


def make_initial_state(question: str, image_paths: list[str] | None = None) -> ResearchState:
    return {
        "question": question,
        "image_paths": image_paths or [],
        "query_plan": None,
        "search_queries": [],
        "research_passes": 0,
        "candidate_sources": [],
        "selected_sources": [],
        "research_brief": None,
        "critique": None,
        "summary": None,
        "vision": None,
        "final_report": None,
        "final_answer": "",
        "errors": [],
    }


def serialize_sources_for_prompt(sources: list[SourceRecord]) -> str:
    if not sources:
        return "[]"
    return json.dumps([source.model_dump() for source in sources], indent=2)


def serialize_issues_for_prompt(issues: list[PipelineIssue]) -> str:
    if not issues:
        return "[]"
    return json.dumps([issue.model_dump() for issue in issues], indent=2)


def append_issues(existing: list[PipelineIssue], new_issues: list[PipelineIssue]) -> list[PipelineIssue]:
    return [*existing, *new_issues]
