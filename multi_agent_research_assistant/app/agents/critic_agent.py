from __future__ import annotations

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.critic_prompt import CRITIC_SYSTEM_PROMPT
from app.schemas import CritiqueReport
from app.state import ResearchState, serialize_issues_for_prompt, serialize_sources_for_prompt


def run_critic(state: ResearchState, config: AppConfig) -> ResearchState:
    research_brief = state.get("research_brief")
    if research_brief is None:
        raise RuntimeError("Critic agent requires a research brief.")

    critique = invoke_structured_model(
        config=config,
        schema=CritiqueReport,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        user_input="\n\n".join(
            [
                f"Question:\n{state['question']}",
                f"Research pass count:\n{state.get('research_passes', 0)} of {config.max_research_passes}",
                f"Selected sources:\n{serialize_sources_for_prompt(state.get('selected_sources', []))}",
                f"Research brief:\n{research_brief.model_dump_json(indent=2)}",
                f"Known pipeline issues:\n{serialize_issues_for_prompt(state.get('errors', []))}",
            ]
        ),
    )

    return {"critique": critique}
