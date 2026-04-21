from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.critic_agent import run_critic
from app.agents.research_agent import run_research
from app.agents.summarizer_agent import run_summarizer
from app.agents.synthesizer_agent import run_synthesizer
from app.agents.vision_agent import run_vision
from app.config import AppConfig, load_config
from app.state import ResearchState


def build_graph(config: AppConfig | None = None):
    app_config = config or load_config()

    graph = StateGraph(ResearchState)
    graph.add_node("research", lambda state: run_research(state, app_config))
    graph.add_node("critic", lambda state: run_critic(state, app_config))
    graph.add_node("summarize", lambda state: run_summarizer(state, app_config))
    graph.add_node("vision", lambda state: run_vision(state, app_config))
    graph.add_node("synthesize", lambda state: run_synthesizer(state, app_config))

    graph.add_edge(START, "research")
    graph.add_edge("research", "critic")
    graph.add_conditional_edges(
        "critic",
        lambda state: _route_after_critique(state, app_config),
        {
            "research": "research",
            "summarize": "summarize",
        },
    )
    graph.add_conditional_edges(
        "summarize",
        _route_after_summary,
        {
            "vision": "vision",
            "synthesize": "synthesize",
        },
    )
    graph.add_edge("vision", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


def _route_after_critique(state: ResearchState, config: AppConfig) -> str:
    critique = state.get("critique")
    needs_revision = critique.needs_revision if critique is not None else False
    research_passes = state.get("research_passes", 0)
    if needs_revision and research_passes < config.max_research_passes:
        return "research"
    return "summarize"


def _route_after_summary(state: ResearchState) -> str:
    if state.get("image_paths"):
        return "vision"
    return "synthesize"
