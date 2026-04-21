from __future__ import annotations

import json

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.synthesizer_prompt import SYNTHESIZER_SYSTEM_PROMPT
from app.schemas import FinalReport, ReportSource, SynthesisDraft
from app.state import ResearchState, serialize_sources_for_prompt


def run_synthesizer(state: ResearchState, config: AppConfig) -> ResearchState:
    summary = state.get("summary")
    critique = state.get("critique")
    if summary is None:
        raise RuntimeError("Synthesizer agent requires a summary.")
    if critique is None:
        raise RuntimeError("Synthesizer agent requires a critique.")

    synthesis = invoke_structured_model(
        config=config,
        schema=SynthesisDraft,
        system_prompt=SYNTHESIZER_SYSTEM_PROMPT,
        user_input="\n\n".join(
            [
                f"Question:\n{state['question']}",
                f"Selected sources:\n{serialize_sources_for_prompt(state.get('selected_sources', []))}",
                f"Summary:\n{summary.model_dump_json(indent=2)}",
                f"Critique:\n{critique.model_dump_json(indent=2)}",
                f"Vision analysis:\n{_serialize_optional_model(state.get('vision'))}",
            ]
        ),
    )

    report_sources = _resolve_report_sources(
        requested_ids=synthesis.source_ids or summary.source_ids,
        available_sources=state.get("selected_sources", []),
    )

    final_report = FinalReport(
        executive_summary=synthesis.executive_summary,
        key_insights=synthesis.key_insights,
        opportunities=synthesis.opportunities,
        risks=synthesis.risks,
        limitations=synthesis.limitations,
        confidence=synthesis.confidence,
        sources=report_sources,
        vision=state.get("vision"),
        issues=state.get("errors", []),
    )

    return {
        "final_report": final_report,
        "final_answer": json.dumps(final_report.model_dump(mode="json"), indent=2),
    }


def _resolve_report_sources(requested_ids: list[str], available_sources) -> list[ReportSource]:
    source_lookup = {source.id: source for source in available_sources}
    selected: list[ReportSource] = []

    for source_id in requested_ids:
        source = source_lookup.get(source_id)
        if source is not None:
            selected.append(ReportSource.from_source(source))

    if selected:
        return selected

    return [ReportSource.from_source(source) for source in available_sources]


def _serialize_optional_model(value) -> str:
    if value is None:
        return "null"
    return value.model_dump_json(indent=2)
