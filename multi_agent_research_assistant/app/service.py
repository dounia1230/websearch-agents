from __future__ import annotations

from typing import Any

from app.config import AppConfig, load_config
from app.graph import build_graph
from app.schemas import FinalReport
from app.state import ResearchState, make_initial_state


def run_workflow(
    *,
    question: str,
    image_paths: list[str] | None = None,
    config: AppConfig | None = None,
    graph: Any | None = None,
) -> ResearchState:
    normalized_question = question.strip()
    if not normalized_question:
        raise ValueError("A research question is required.")

    app_config = config or load_config()
    compiled_graph = graph or build_graph(app_config)
    return compiled_graph.invoke(make_initial_state(normalized_question, image_paths=image_paths or []))


def get_final_report(state: ResearchState) -> FinalReport:
    final_report = state.get("final_report")
    if final_report is None:
        raise RuntimeError("The workflow completed without producing a final report.")
    return final_report
