from __future__ import annotations

from app.schemas import SourceRecord
from app.utils.source_quality import evaluate_source_quality


def test_evaluate_source_quality_rewards_official_sources() -> None:
    source = SourceRecord(
        id="S1",
        title="Official report",
        url="https://www.nasa.gov/report",
        snippet="Detailed official summary.",
        raw_content="x" * 1200,
        extracted_content="",
        source_type="web",
        search_score=0.8,
    )

    evaluated = evaluate_source_quality(source, minimum_score=0.55)

    assert evaluated.included is True
    assert evaluated.quality_score is not None
    assert evaluated.quality_score >= 0.55


def test_evaluate_source_quality_penalizes_spammy_sources() -> None:
    source = SourceRecord(
        id="S2",
        title="Best cheap affiliate list",
        url="https://cheap-affiliate.example.com/top-10",
        snippet="Buy now.",
        raw_content="short",
        extracted_content="",
        source_type="web",
        search_score=0.1,
    )

    evaluated = evaluate_source_quality(source, minimum_score=0.55)

    assert evaluated.included is False
    assert evaluated.quality_label == "low"
