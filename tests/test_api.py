from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api import create_app
from app.config import AppConfig
from app.schemas import FinalReport, ReportSource


def _config() -> AppConfig:
    return AppConfig(
        llm_provider="ollama",
        text_model="qwen3:8b",
        vision_model="llama3.2-vision:latest",
        embedding_model="nomic-embed-text:latest",
        ollama_base_url="http://localhost:11434",
        openai_api_key="",
        openai_base_url="",
        anthropic_api_key="",
        groq_api_key="",
        tavily_api_key="test",
        max_search_results=5,
        max_reader_results=2,
        max_research_passes=2,
        max_follow_up_queries=2,
        max_generation_tokens=400,
        max_source_content_chars=2000,
        max_reader_content_chars=4000,
        request_timeout_seconds=20,
        tavily_search_depth="advanced",
        tavily_topic="general",
        min_source_quality_score=0.55,
        min_intent_alignment_score=0.3,
        min_critic_relevance_score=0.55,
        min_critic_overall_score=0.6,
        retrieval_top_k=3,
        private_data_dir=None,
        chroma_persist_dir=None,
        chroma_collection_name="test",
    )


def _report() -> FinalReport:
    return FinalReport(
        executive_summary="A concise analyst summary.",
        key_insights=["Insight 1"],
        opportunities=["Opportunity 1"],
        risks=["Risk 1"],
        confidence=0.88,
        sources=[
            ReportSource(
                id="S1",
                title="Reuters Brief",
                url="https://www.reuters.com",
                source_type="web",
                quality_score=0.91,
                quality_label="high",
            )
        ],
    )


class DummyGraph:
    def __init__(self) -> None:
        self.invocations: list[dict] = []

    def invoke(self, state: dict) -> dict:
        self.invocations.append(state)
        for image_path in state.get("image_paths", []):
            assert Path(image_path).exists()
        return {
            **state,
            "research_passes": 1,
            "final_report": _report(),
        }


def test_health_endpoint_reports_runtime_config() -> None:
    app = create_app(config=_config(), graph=DummyGraph())

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["llm_provider"] == "ollama"
    assert response.json()["text_model"] == "qwen3:8b"


def test_research_endpoint_returns_structured_report() -> None:
    graph = DummyGraph()
    app = create_app(config=_config(), graph=graph)

    with TestClient(app) as client:
        response = client.post(
            "/research",
            json={"question": "Analyze AI research assistants.", "image_paths": []},
        )

    assert response.status_code == 200
    assert response.json()["report"]["executive_summary"] == "A concise analyst summary."
    assert graph.invocations[0]["question"] == "Analyze AI research assistants."


def test_research_upload_endpoint_persists_uploaded_images_for_the_workflow() -> None:
    graph = DummyGraph()
    app = create_app(config=_config(), graph=graph)

    with TestClient(app) as client:
        response = client.post(
            "/research/upload",
            data={"question": "Analyze this uploaded chart."},
            files=[("files", ("chart.png", b"fake-image-data", "image/png"))],
        )

    assert response.status_code == 200
    assert response.json()["image_paths"]
    assert graph.invocations[0]["image_paths"]


def test_research_endpoint_rejects_blank_questions() -> None:
    app = create_app(config=_config(), graph=DummyGraph())

    with TestClient(app) as client:
        response = client.post("/research", json={"question": "   ", "image_paths": []})

    assert response.status_code == 422
