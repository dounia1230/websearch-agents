from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from app.schemas.research import FinalReport, StrictModel


class HealthResponse(StrictModel):
    status: Literal["ok"] = "ok"
    llm_provider: str
    text_model: str
    vision_model: str


class ResearchRequest(StrictModel):
    question: str = Field(min_length=1, description="Research question to send through the orchestrator.")
    image_paths: list[str] = Field(
        default_factory=list,
        description="Optional existing local image paths for the multimodal path.",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("question must not be empty.")
        return normalized


class ResearchResponse(StrictModel):
    question: str
    image_paths: list[str] = Field(default_factory=list)
    research_passes: int = 0
    report: FinalReport
