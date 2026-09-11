from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import AppConfig, load_config
from app.graph import build_graph
from app.schemas import HealthResponse, ResearchRequest, ResearchResponse
from app.service import get_final_report, run_workflow


def create_app(config: AppConfig | None = None, graph: Any | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _ensure_runtime(app, config=config, graph=graph)
        yield

    app = FastAPI(
        title="Multi-Agent Research Assistant API",
        version="0.1.0",
        description="FastAPI wrapper around the LangGraph-based multi-agent research workflow.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health(request: Request) -> HealthResponse:
        runtime_config = _ensure_runtime(request.app)
        return HealthResponse(
            llm_provider=runtime_config.llm_provider,
            text_model=runtime_config.text_model,
            vision_model=runtime_config.vision_model,
        )

    @app.post("/research", response_model=ResearchResponse)
    async def research(request_payload: ResearchRequest, request: Request) -> ResearchResponse:
        return _run_and_build_response(
            app=request.app,
            question=request_payload.question,
            image_paths=request_payload.image_paths,
        )

    @app.post("/research/upload", response_model=ResearchResponse)
    async def research_upload(request: Request) -> ResearchResponse:
        form = await request.form()
        question = str(form.get("question") or "")
        normalized_question = question.strip()
        if not normalized_question:
            raise HTTPException(status_code=422, detail="question must not be empty.")

        uploads = [
            value
            for value in form.getlist("files")
            if hasattr(value, "filename") and hasattr(value, "file")
        ]
        with TemporaryDirectory(prefix="multi-agent-research-") as temp_dir:
            image_paths = await _save_uploads(uploads, Path(temp_dir))
            return _run_and_build_response(
                app=request.app,
                question=normalized_question,
                image_paths=image_paths,
            )

    return app


def _run_and_build_response(
    *,
    app: FastAPI,
    question: str,
    image_paths: list[str],
) -> ResearchResponse:
    runtime_config = _ensure_runtime(app)

    try:
        result = run_workflow(
            question=question,
            image_paths=image_paths,
            config=runtime_config,
            graph=app.state.workflow_graph,
        )
        final_report = get_final_report(result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Research workflow failed: {exc}") from exc

    return ResearchResponse(
        question=question.strip(),
        image_paths=image_paths,
        research_passes=result.get("research_passes", 0),
        report=final_report,
    )


def _ensure_runtime(
    app: FastAPI,
    *,
    config: AppConfig | None = None,
    graph: Any | None = None,
) -> AppConfig:
    existing_config = getattr(app.state, "app_config", None)
    existing_graph = getattr(app.state, "workflow_graph", None)
    if existing_config is not None and existing_graph is not None:
        return existing_config

    load_dotenv()
    runtime_config = config or load_config()
    runtime_graph = graph or build_graph(runtime_config)
    app.state.app_config = runtime_config
    app.state.workflow_graph = runtime_graph
    return runtime_config


async def _save_uploads(files: list[UploadFile], temp_dir: Path) -> list[str]:
    image_paths: list[str] = []
    for index, upload in enumerate(files, start=1):
        file_name = Path(upload.filename or f"upload-{index}").name
        destination = temp_dir / f"{index:02d}-{file_name}"
        with destination.open("wb") as output_file:
            shutil.copyfileobj(upload.file, output_file)
        image_paths.append(str(destination))
        await upload.close()
    return image_paths


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "app.api:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
