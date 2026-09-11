# Multi-Agent Research Assistant

This repository implements a typed, explainable research workflow built around LangGraph, LangChain, Tavily, Jina Reader, and an optional LlamaIndex retrieval path for private documents.

Core flow:

1. `planner_agent`
2. `research_agent`
3. `critic_agent`
4. `summarizer_agent`
5. `vision_agent` when image input exists
6. `synthesizer_agent`

The pipeline is opinionated around:

- structured JSON outputs
- explicit source preservation
- source quality filtering
- configurable LLM providers
- optional multimodal analysis
- optional private-data retrieval with LlamaIndex + ChromaDB

## Project Structure

```text
multi_agent_research_assistant/
|
|-- app/
|   |-- agents/
|   |-- llm/
|   |-- prompts/
|   |-- schemas/
|   |-- tools/
|   |-- utils/
|   |-- config.py
|   |-- graph.py
|   |-- main.py
|   `-- state.py
|
|-- README.md
`-- requirements.txt
```

## Features

- `LangGraph` orchestrates the research and critique loop.
- `Planner Agent` interprets user intent and generates focused Tavily searches before retrieval starts.
- `LangChain` drives prompt execution and model interaction.
- `Tavily` provides web search results.
- `Jina Reader` converts selected web pages into cleaner text.
- `LlamaIndex` + `ChromaDB` can retrieve context from local/private documents.
- Structured `pydantic` schemas keep agent outputs predictable.
- Source quality heuristics filter suspicious or thin sources before synthesis.
- Planner-aware intent screening and critic-side relevance scoring filter out broad but off-context sources.
- Optional image input triggers a separate vision analysis step.

## Configuration

Copy the sample environment file pattern below into `.env` or set equivalent environment variables:

```env
LLM_PROVIDER=ollama
TEXT_MODEL=qwen3:8b
VISION_MODEL=llama3.2-vision:latest
EMBEDDING_MODEL=nomic-embed-text:latest
OLLAMA_BASE_URL=http://localhost:11434
TAVILY_API_KEY=your_tavily_key

MAX_SEARCH_RESULTS=6
MAX_READER_RESULTS=4
MAX_RESEARCH_PASSES=2
MAX_FOLLOW_UP_QUERIES=2
MAX_GENERATION_TOKENS=1200
MAX_SOURCE_CONTENT_CHARS=2500
MAX_READER_CONTENT_CHARS=4500
MIN_SOURCE_QUALITY_SCORE=0.55
MIN_INTENT_ALIGNMENT_SCORE=0.30
MIN_CRITIC_RELEVANCE_SCORE=0.55
MIN_CRITIC_OVERALL_SCORE=0.60
REQUEST_TIMEOUT_SECONDS=30
TAVILY_SEARCH_DEPTH=advanced
TAVILY_TOPIC=general

PRIVATE_DATA_DIR=
RETRIEVAL_TOP_K=3
CHROMA_PERSIST_DIR=
CHROMA_COLLECTION_NAME=research_assistant
```

Supported `LLM_PROVIDER` values:

- `ollama`

The defaults are tuned for local Ollama usage, as required by `AGENTS.md`.

## Setup

```powershell
cd multi_agent_research_assistant
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you are using Ollama locally:

```powershell
ollama pull qwen3:8b
ollama pull llama3.2-vision:latest
ollama pull nomic-embed-text:latest
```

## Run

Text-only research:

```powershell
python -m app.main "What are the main tradeoffs of sodium-ion batteries versus lithium-ion batteries?"
```

Text plus image:

```powershell
python -m app.main "What does this chart imply about the market?" --image C:\path\to\chart.png
```

The CLI prints a final structured JSON report containing:

- `executive_summary`
- `key_insights`
- `opportunities`
- `risks`
- `limitations`
- `confidence`
- `sources`
- `vision` when images were analyzed
- `issues`

## FastAPI Server

Run the workflow as an HTTP API:

```powershell
cd multi_agent_research_assistant
uvicorn app.api:app --reload
```

Or:

```powershell
python -m app.api
```

Available endpoints:

- `GET /health`
- `POST /research`
- `POST /research/upload`

JSON request example:

```json
{
  "question": "Assess the market opportunity for AI-native research assistants in higher education.",
  "image_paths": []
}
```

Multipart upload example:

```powershell
curl -X POST "http://127.0.0.1:8000/research/upload" ^
  -F "question=Analyze this chart and summarize the implications" ^
  -F "files=@C:\path\to\chart.png"
```

## Frontend Dashboard

The React dashboard lives in the repository-level `frontend/` directory. It presents the workflow as a three-panel research workspace rather than a chat interface:

- run controls and optional image upload
- orchestrator progress with a status card for every agent
- a structured final report with confidence and clickable sources

Run it in a separate terminal after starting the API:

```powershell
cd ..\frontend
npm install
npm run dev
```

The browser client calls `POST /research` for text-only runs and `POST /research/upload` when an image is attached. Set `VITE_API_BASE_URL` in `frontend/.env` when the API is not available at `http://127.0.0.1:8000`.

## Tests

```powershell
python -m pytest ..\tests
```

## Notes

- Web failures are tracked as structured pipeline issues where recovery is possible.
- Source URLs and titles are preserved throughout the workflow.
- Private retrieval is optional and only activates when `PRIVATE_DATA_DIR` is configured.
- This is still an MVP workflow. Agent progress in the dashboard is currently animated client-side; a future event-streaming API can replace that simulation with live graph events.
