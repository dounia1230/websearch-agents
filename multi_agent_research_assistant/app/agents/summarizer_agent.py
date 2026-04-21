from __future__ import annotations

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.summarizer_prompt import SUMMARIZER_SYSTEM_PROMPT
from app.schemas import SummaryReport
from app.state import ResearchState, serialize_sources_for_prompt


def run_summarizer(state: ResearchState, config: AppConfig) -> ResearchState:
    research_brief = state.get("research_brief")
    critique = state.get("critique")
    if research_brief is None:
        raise RuntimeError("Summarizer agent requires a research brief.")
    if critique is None:
        raise RuntimeError("Summarizer agent requires a critique.")

    summary = invoke_structured_model(
        config=config,
        schema=SummaryReport,
        system_prompt=SUMMARIZER_SYSTEM_PROMPT,
        user_input="\n\n".join(
            [
                f"Question:\n{state['question']}",
                f"Selected sources:\n{serialize_sources_for_prompt(state.get('selected_sources', []))}",
                f"Research brief:\n{research_brief.model_dump_json(indent=2)}",
                f"Critique:\n{critique.model_dump_json(indent=2)}",
            ]
        ),
    )

    return {"summary": summary}
