from __future__ import annotations

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from app.schemas import PlannerOutput
from app.state import ResearchState


def run_planner(state: ResearchState, config: AppConfig) -> ResearchState:
    prior_plan = state.get("query_plan")
    prior_critique = state.get("critique")

    planner_output = invoke_structured_model(
        config=config,
        schema=PlannerOutput,
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_input="\n\n".join(
            [
                f"User question:\n{state['question']}",
                "Previous plan:\n" + ("null" if prior_plan is None else prior_plan.model_dump_json(indent=2)),
                "Previous critique:\n"
                + ("null" if prior_critique is None else prior_critique.model_dump_json(indent=2)),
            ]
        ),
    )

    return {
        "query_plan": planner_output,
        "search_queries": planner_output.search_queries,
    }
