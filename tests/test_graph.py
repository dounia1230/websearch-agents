from __future__ import annotations

from app.graph import _route_after_critique, _route_after_summary
from app.schemas import CritiqueReport
from app.state import make_initial_state


class DummyConfig:
    max_research_passes = 2


def test_route_after_critique_revisits_research_when_requested() -> None:
    state = make_initial_state("test")
    state["research_passes"] = 1
    state["critique"] = CritiqueReport(
        needs_revision=True,
        rationale="Coverage is weak.",
        missing_angles=["regulation"],
        unsupported_or_weak_claims=[],
        follow_up_queries=["latest regulation market analysis"],
        confidence=0.7,
    )

    route = _route_after_critique(state, DummyConfig())

    assert route == "research"


def test_route_after_summary_only_uses_vision_when_images_exist() -> None:
    text_only_state = make_initial_state("text only")
    multimodal_state = make_initial_state("with image", image_paths=["chart.png"])

    assert _route_after_summary(text_only_state) == "synthesize"
    assert _route_after_summary(multimodal_state) == "vision"
