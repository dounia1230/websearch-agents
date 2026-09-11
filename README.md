# Multi-Agent Research Assistant

An explainable research workflow that plans a query, retrieves and critiques sources, summarizes evidence, optionally analyzes images, and synthesizes a structured report.

The repository contains:

- `multi_agent_research_assistant/` — Python, LangGraph, LangChain, FastAPI, Tavily, and optional LlamaIndex/ChromaDB backend
- `frontend/` — React, TypeScript, Tailwind CSS, shadcn/ui, and Lucide dashboard
- `tests/` — fast unit and API tests
- `docs/` — architecture notes

## Quick start

Start the backend:

```powershell
cd multi_agent_research_assistant
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.api:app --reload
```

In another terminal, start the dashboard:

```powershell
cd frontend
npm install
npm run dev
```

The frontend targets `http://127.0.0.1:8000` by default. Copy `frontend/.env.example` to `frontend/.env` to use a different API URL.

See [the backend guide](multi_agent_research_assistant/README.md) and [architecture notes](docs/architecture.md) for configuration and workflow details.
