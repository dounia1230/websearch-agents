from __future__ import annotations

from app.config import AppConfig
from app.llm import invoke_structured_model
from app.prompts.vision_prompt import VISION_SYSTEM_PROMPT
from app.schemas import PipelineIssue, VisionReport
from app.state import ResearchState, append_issues


def run_vision(state: ResearchState, config: AppConfig) -> ResearchState:
    image_paths = state.get("image_paths", [])
    if not image_paths:
        return {}

    try:
        vision = invoke_structured_model(
            config=config,
            schema=VisionReport,
            system_prompt=VISION_SYSTEM_PROMPT,
            user_input="\n\n".join(
                [
                    f"Question:\n{state['question']}",
                    "Analyze the provided image set. If multiple images exist, summarize cross-image observations carefully.",
                ]
            ),
            image_paths=image_paths,
        )
        return {"vision": vision}
    except Exception as exc:
        issue = PipelineIssue(
            stage="vision",
            message=f"Vision analysis failed: {exc}",
            recoverable=True,
            details={"image_paths": image_paths},
        )
        fallback = VisionReport(
            visible_facts=[],
            ocr_text=[],
            interpretation=[],
            limitations=[f"Vision analysis could not be completed: {exc}"],
            confidence=0.0,
        )
        return {
            "vision": fallback,
            "errors": append_issues(state.get("errors", []), [issue]),
        }
