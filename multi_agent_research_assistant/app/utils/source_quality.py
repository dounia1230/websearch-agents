from __future__ import annotations

from collections.abc import Iterable
import re
from urllib.parse import urlparse

from app.schemas import PlannerOutput, SourceAssessment, SourceRecord

PREFERRED_TLDS = (".gov", ".edu", ".ac.uk")
SUSPICIOUS_TERMS = (
    "affiliate",
    "coupon",
    "promo",
    "sponsored",
    "betting",
    "casino",
    "top-10",
    "best-",
    "cheap",
    "discount",
)
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "about",
    "what",
    "when",
    "where",
    "who",
    "your",
    "their",
    "have",
    "mean",
    "does",
    "will",
    "would",
    "could",
    "should",
    "using",
    "user",
    "real",
    "intent",
}


def evaluate_source_quality(source: SourceRecord, minimum_score: float) -> SourceRecord:
    score = 0.45
    rationale: list[str] = []
    domain = _extract_domain(source.url)
    evidence_text = " ".join(
        part for part in [source.title, source.snippet, source.raw_content, source.extracted_content] if part
    ).lower()

    if source.search_score is not None:
        score += max(0.0, min(source.search_score, 1.0)) * 0.2
        rationale.append("Search ranking contributed to quality scoring.")

    if domain.endswith(PREFERRED_TLDS):
        score += 0.25
        rationale.append("Domain suggests an official or academic source.")
    elif any(token in domain for token in ("reuters.com", "apnews.com", "nature.com", "who.int", "oecd.org")):
        score += 0.2
        rationale.append("Domain is commonly associated with reputable reporting or institutions.")

    if len(source.extracted_content or source.raw_content or "") >= 600:
        score += 0.1
        rationale.append("Source contains substantial extractable content.")
    elif len(source.snippet) < 60:
        score -= 0.1
        rationale.append("Only a thin snippet is available.")

    if any(term in domain or term in evidence_text for term in SUSPICIOUS_TERMS):
        score -= 0.35
        rationale.append("Suspicious commercial or spam-like indicators were detected.")

    if not source.title.strip():
        score -= 0.15
        rationale.append("Missing title lowers traceability.")
    if not source.url.strip():
        score -= 0.25
        rationale.append("Missing URL lowers traceability.")

    normalized_score = round(max(0.0, min(score, 1.0)), 3)
    quality_label = _label_for_score(normalized_score)
    if not rationale:
        rationale.append("Default heuristic quality assessment applied.")

    return source.model_copy(
        update={
            "quality_score": normalized_score,
            "quality_label": quality_label,
            "quality_rationale": " ".join(rationale),
            "included": normalized_score >= minimum_score,
        }
    )


def deduplicate_sources(sources: Iterable[SourceRecord]) -> list[SourceRecord]:
    merged: dict[str, SourceRecord] = {}
    for source in sources:
        key = _dedupe_key(source)
        existing = merged.get(key)
        if existing is None:
            merged[key] = source
            continue
        merged[key] = _prefer_richer_source(existing, source)
    return list(merged.values())


def merge_sources(existing: Iterable[SourceRecord], new_sources: Iterable[SourceRecord]) -> list[SourceRecord]:
    return deduplicate_sources([*existing, *new_sources])


def evaluate_source_intent_alignment(
    source: SourceRecord,
    query_plan: PlannerOutput,
    minimum_score: float,
) -> SourceRecord:
    text = " ".join(
        part for part in [source.title, source.snippet, source.raw_content, source.extracted_content] if part
    ).lower()
    rationale: list[str] = []
    score = 0.45

    include_hits = _count_topic_hits(text, query_plan.include_topics)
    if query_plan.include_topics:
        if include_hits > 0:
            score += min(include_hits * 0.12, 0.3)
            rationale.append("Matched planner include topics.")
        else:
            score -= 0.18
            rationale.append("Missed the planner's expected topic cues.")

    exclude_hits = _count_topic_hits(text, query_plan.exclude_topics)
    if exclude_hits > 0:
        score -= min(exclude_hits * 0.18, 0.45)
        rationale.append("Matched excluded or distracting topics.")

    intent_terms = _extract_terms(query_plan.interpreted_query, query_plan.user_intent)
    intent_matches = sum(1 for term in intent_terms if term in text)
    if intent_matches >= 2:
        score += 0.18
        rationale.append("Matched multiple interpreted-intent terms.")
    elif intent_matches == 1:
        score += 0.08
        rationale.append("Matched one interpreted-intent term.")
    else:
        score -= 0.12
        rationale.append("Showed weak lexical overlap with the interpreted intent.")

    normalized_score = round(max(0.0, min(score, 1.0)), 3)
    return source.model_copy(
        update={
            "intent_alignment_score": normalized_score,
            "intent_alignment_rationale": " ".join(rationale) or "Default intent-alignment heuristic applied.",
            "included": source.included and normalized_score >= minimum_score,
        }
    )


def apply_source_assessment(
    source: SourceRecord,
    assessment: SourceAssessment,
    minimum_relevance_score: float,
    minimum_overall_score: float,
) -> SourceRecord:
    overall_score = assessment.overall_score
    include = (
        source.included
        and assessment.include
        and assessment.relevance_to_user_intent >= minimum_relevance_score
        and overall_score >= minimum_overall_score
    )
    return source.model_copy(
        update={
            "authority_score": assessment.authority,
            "relevance_to_user_intent_score": assessment.relevance_to_user_intent,
            "specificity_score": assessment.specificity,
            "recency_score": assessment.recency,
            "evidence_score": assessment.evidence,
            "clarity_score": assessment.clarity,
            "critic_score": overall_score,
            "critic_rationale": assessment.rationale,
            "included": include,
        }
    )


def _prefer_richer_source(left: SourceRecord, right: SourceRecord) -> SourceRecord:
    left_weight = _source_richness(left)
    right_weight = _source_richness(right)
    preferred = right if right_weight > left_weight else left
    secondary = left if preferred is right else right
    update = {
        "snippet": preferred.snippet or secondary.snippet,
        "raw_content": preferred.raw_content or secondary.raw_content,
        "extracted_content": preferred.extracted_content or secondary.extracted_content,
        "quality_score": preferred.quality_score if preferred.quality_score is not None else secondary.quality_score,
        "quality_label": preferred.quality_label if preferred.quality_score is not None else secondary.quality_label,
        "quality_rationale": preferred.quality_rationale
        if preferred.quality_rationale != "Quality has not been evaluated yet."
        else secondary.quality_rationale,
        "intent_alignment_score": preferred.intent_alignment_score
        if preferred.intent_alignment_score is not None
        else secondary.intent_alignment_score,
        "intent_alignment_rationale": preferred.intent_alignment_rationale
        if preferred.intent_alignment_score is not None
        else secondary.intent_alignment_rationale,
        "authority_score": preferred.authority_score
        if preferred.authority_score is not None
        else secondary.authority_score,
        "relevance_to_user_intent_score": preferred.relevance_to_user_intent_score
        if preferred.relevance_to_user_intent_score is not None
        else secondary.relevance_to_user_intent_score,
        "specificity_score": preferred.specificity_score
        if preferred.specificity_score is not None
        else secondary.specificity_score,
        "recency_score": preferred.recency_score
        if preferred.recency_score is not None
        else secondary.recency_score,
        "evidence_score": preferred.evidence_score
        if preferred.evidence_score is not None
        else secondary.evidence_score,
        "clarity_score": preferred.clarity_score
        if preferred.clarity_score is not None
        else secondary.clarity_score,
        "critic_score": preferred.critic_score if preferred.critic_score is not None else secondary.critic_score,
        "critic_rationale": preferred.critic_rationale or secondary.critic_rationale,
        "included": preferred.included or secondary.included,
        "metadata": {**secondary.metadata, **preferred.metadata},
    }
    return preferred.model_copy(update=update)


def _source_richness(source: SourceRecord) -> int:
    return sum(
        len(value)
        for value in (
            source.title,
            source.snippet,
            source.raw_content,
            source.extracted_content,
        )
    )


def _dedupe_key(source: SourceRecord) -> str:
    if source.url:
        return source.url.rstrip("/").lower()
    return source.title.strip().lower()


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    return (urlparse(url).netloc or "").lower()


def _label_for_score(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _count_topic_hits(text: str, topics: list[str]) -> int:
    return sum(1 for topic in topics if topic.strip().lower() and topic.strip().lower() in text)


def _extract_terms(*texts: str) -> set[str]:
    terms: set[str] = set()
    for text in texts:
        for token in re.findall(r"[a-z0-9][a-z0-9\-]{1,}", text.lower()):
            if token not in STOPWORDS:
                terms.add(token)
    return terms
