from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PipelineIssue(StrictModel):
    stage: str = Field(description="Pipeline stage that raised the issue.")
    message: str = Field(description="Human-readable error or warning message.")
    recoverable: bool = Field(default=True, description="Whether the pipeline can continue.")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured debugging details that should be preserved for traceability.",
    )


class SourceRecord(StrictModel):
    id: str = Field(description="Stable source identifier such as S1 or P1.")
    title: str = Field(description="Source title.")
    url: str = Field(description="Canonical URL or file URI.")
    snippet: str = Field(default="", description="Short search snippet or retrieval excerpt.")
    raw_content: str = Field(default="", description="Raw source content when available.")
    extracted_content: str = Field(
        default="",
        description="Cleaned extracted text content, such as Jina Reader output or retrieved chunk text.",
    )
    source_type: Literal["web", "private_data"] = Field(
        description="Whether the source came from web search or local/private retrieval.",
    )
    search_score: float | None = Field(
        default=None,
        description="Original search-provider ranking score when available.",
    )
    quality_score: float | None = Field(
        default=None,
        description="Normalized 0-1 quality score assigned by the pipeline.",
    )
    quality_label: Literal["high", "medium", "low", "unknown"] = Field(
        default="unknown",
        description="Human-readable quality bucket derived from quality_score.",
    )
    quality_rationale: str = Field(
        default="Quality has not been evaluated yet.",
        description="Short explanation for the quality decision.",
    )
    intent_alignment_score: float | None = Field(
        default=None,
        description="Heuristic 0-1 score for how well the source matches the interpreted query plan.",
    )
    intent_alignment_rationale: str = Field(
        default="Intent alignment has not been evaluated yet.",
        description="Short explanation for the planner-based alignment heuristic.",
    )
    authority_score: float | None = Field(
        default=None,
        description="Critic-assigned 0-1 authority score.",
    )
    relevance_to_user_intent_score: float | None = Field(
        default=None,
        description="Critic-assigned 0-1 relevance score against the interpreted user intent.",
    )
    specificity_score: float | None = Field(
        default=None,
        description="Critic-assigned 0-1 specificity score.",
    )
    recency_score: float | None = Field(
        default=None,
        description="Critic-assigned 0-1 recency score.",
    )
    evidence_score: float | None = Field(
        default=None,
        description="Critic-assigned 0-1 evidence score.",
    )
    clarity_score: float | None = Field(
        default=None,
        description="Critic-assigned 0-1 clarity score.",
    )
    critic_score: float | None = Field(
        default=None,
        description="Derived overall critic score based on the scoring dimensions.",
    )
    critic_rationale: str | None = Field(
        default=None,
        description="Critic explanation for keeping or rejecting the source.",
    )
    included: bool = Field(
        default=True,
        description="Whether the source remains eligible for downstream reasoning.",
    )
    extraction_status: Literal["not_requested", "success", "failed"] = Field(
        default="not_requested",
        description="Whether content extraction was attempted and if it succeeded.",
    )
    extraction_error: str | None = Field(
        default=None,
        description="Structured extraction error summary when extraction failed.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional trace metadata such as file path or retrieval score.",
    )


class ResearchBrief(StrictModel):
    query_scope: str = Field(description="How the question was interpreted for research.")
    key_findings: list[str] = Field(
        default_factory=list,
        description="Evidence-backed findings with inline source ids such as [S1].",
    )
    source_assessment: list[str] = Field(
        default_factory=list,
        description="Short notes about source strength, coverage, or disagreement.",
    )
    open_questions: list[str] = Field(
        default_factory=list,
        description="What remains uncertain or weakly supported.",
    )
    recommended_follow_up: list[str] = Field(
        default_factory=list,
        description="Targeted follow-up angles or query ideas for another pass.",
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the current brief.")


class PlannerOutput(StrictModel):
    interpreted_query: str = Field(description="Intent-aware restatement of the user's real research ask.")
    user_intent: str = Field(description="Short explanation of what the user is actually trying to learn.")
    search_queries: list[str] = Field(
        min_length=3,
        max_length=5,
        description="Three to five precise search queries for Tavily.",
    )
    include_topics: list[str] = Field(
        default_factory=list,
        description="Concepts or entities that should be present in relevant sources when applicable.",
    )
    exclude_topics: list[str] = Field(
        default_factory=list,
        description="Concepts or contexts that should usually be filtered out.",
    )
    notes: str = Field(description="Short planning notes or caveats for retrieval.")


class SourceAssessment(StrictModel):
    source_id: str = Field(description="Source identifier such as S1 or P1.")
    authority: float = Field(ge=0.0, le=1.0)
    relevance_to_user_intent: float = Field(ge=0.0, le=1.0)
    specificity: float = Field(ge=0.0, le=1.0)
    recency: float = Field(ge=0.0, le=1.0)
    evidence: float = Field(ge=0.0, le=1.0)
    clarity: float = Field(ge=0.0, le=1.0)
    include: bool = Field(description="Whether the source should remain in the filtered source set.")
    rationale: str = Field(description="Why the source should be kept or rejected.")

    @property
    def overall_score(self) -> float:
        dimensions = [
            self.authority,
            self.relevance_to_user_intent,
            self.specificity,
            self.recency,
            self.evidence,
            self.clarity,
        ]
        return round(sum(dimensions) / len(dimensions), 3)


class CritiqueReport(StrictModel):
    needs_revision: bool = Field(description="Whether another research pass is warranted.")
    rationale: str = Field(description="Why the brief is sufficient or insufficient.")
    missing_angles: list[str] = Field(
        default_factory=list,
        description="Important angles missing from the current brief.",
    )
    unsupported_or_weak_claims: list[str] = Field(
        default_factory=list,
        description="Claims that appear weakly supported or too broad.",
    )
    follow_up_queries: list[str] = Field(
        default_factory=list,
        description="Search queries that should materially improve coverage if another pass happens.",
    )
    source_assessments: list[SourceAssessment] = Field(
        default_factory=list,
        description="Per-source scoring across authority, relevance, specificity, recency, evidence, and clarity.",
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the critique decision.")


class SummaryReport(StrictModel):
    executive_summary: str = Field(description="Compact decision-ready summary of the research.")
    key_insights: list[str] = Field(
        default_factory=list,
        description="Most important findings, with inline source ids in each item.",
    )
    opportunities: list[str] = Field(
        default_factory=list,
        description="Potential upside, actions, or implications supported by the evidence.",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Downside, uncertainty, or reliability concerns supported by the evidence.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Known evidence gaps or scope limits.",
    )
    source_ids: list[str] = Field(
        default_factory=list,
        description="Source identifiers that support the summary.",
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the summary.")


class VisionReport(StrictModel):
    visible_facts: list[str] = Field(
        default_factory=list,
        description="Directly visible facts from the image input.",
    )
    ocr_text: list[str] = Field(
        default_factory=list,
        description="Text that appears visibly present in the image, when legible.",
    )
    interpretation: list[str] = Field(
        default_factory=list,
        description="Reasonable interpretation of the image contents grounded in visible evidence.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Image quality, ambiguity, or missing context caveats.",
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the visual analysis.")


class SynthesisDraft(StrictModel):
    executive_summary: str = Field(description="Final concise answer to the user's question.")
    key_insights: list[str] = Field(
        default_factory=list,
        description="Final synthesized findings with inline source ids.",
    )
    opportunities: list[str] = Field(
        default_factory=list,
        description="Decision-relevant opportunities or implications.",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Decision-relevant risks, tradeoffs, or uncertainty.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Residual limitations or unanswered questions.",
    )
    source_ids: list[str] = Field(
        default_factory=list,
        description="Source identifiers explicitly relied upon in the final synthesis.",
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the final synthesis.")


class ReportSource(StrictModel):
    id: str
    title: str
    url: str
    source_type: Literal["web", "private_data"]
    quality_score: float | None = None
    quality_label: Literal["high", "medium", "low", "unknown"] = "unknown"
    relevance_score: float | None = None
    critic_score: float | None = None

    @classmethod
    def from_source(cls, source: SourceRecord) -> "ReportSource":
        return cls(
            id=source.id,
            title=source.title,
            url=source.url,
            source_type=source.source_type,
            quality_score=source.quality_score,
            quality_label=source.quality_label,
            relevance_score=source.relevance_to_user_intent_score,
            critic_score=source.critic_score,
        )


class FinalReport(StrictModel):
    executive_summary: str
    key_insights: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[ReportSource] = Field(default_factory=list)
    vision: VisionReport | None = None
    issues: list[PipelineIssue] = Field(default_factory=list)
