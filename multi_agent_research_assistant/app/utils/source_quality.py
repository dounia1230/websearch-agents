from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urlparse

from app.schemas import SourceRecord

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
