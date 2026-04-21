

## Project
Multi-Agent Research Assistant

This repository implements a multi-agent research system that:
- accepts a user research query
- searches and collects web information
- filters unreliable sources
- extracts structured insights
- optionally analyzes user-provided images
- synthesizes a decision-ready report

Primary goal:
Build a reliable, explainable research workflow rather than a generic chatbot.

---

## Core Architecture

Main workflow:
1. Research Agent
2. Critic Agent
3. Summarizer Agent
4. Vision Agent (optional, when image input exists)
5. Synthesizer Agent
6. Orchestrator / graph execution

The system should favor:
- structured outputs
- explicit source handling
- deterministic pipelines where possible
- small, testable modules
- minimal hidden behavior

---

## Model Policy

Default text model:
- `qwen3:8b` via Ollama

Vision model:
- `llama3.2-vision:latest`

Embeddings model:
- `nomic-embed-text:latest`

Use `qwen3:8b` for:
- planning
- source critique
- structured extraction
- report synthesis

Use `llama3.2-vision:latest` only for:
- image understanding
- screenshot/chart/image analysis
- extracting visible information from user-uploaded images

Do not use vision models for normal text-only tasks unless explicitly necessary.

Do not use coding-specialized models like `codellama` for research analysis logic unless the task is specifically code generation or code refactoring.

---

## Engineering Priorities

Always optimize for:
1. correctness
2. traceability
3. maintainability
4. clear folder structure
5. typed interfaces
6. small composable functions
7. readable prompts
8. predictable outputs

Avoid:
- giant files
- over-engineered abstractions
- magic constants without explanation
- deeply nested business logic
- prompt strings scattered randomly across the codebase
- silent failures
- hidden global state unless justified

---

## Output Requirements

When implementing agents:
- prefer structured JSON or typed model outputs
- include confidence fields where appropriate
- preserve source metadata
- never discard URLs/titles silently
- keep extraction schema consistent across agents

Expected final outputs should usually include:
- executive_summary
- key_insights
- opportunities
- risks
- confidence
- sources

If ambiguity exists, preserve uncertainty explicitly instead of pretending confidence.

---

## Source Handling Rules

Treat web information carefully.

Preferred sources:
- official organizations
- government sites
- research institutions
- reputable news outlets
- high-quality technical blogs when directly relevant

Lower trust sources:
- SEO spam
- thin affiliate content
- anonymous opinion posts
- duplicated scraped articles

Every source object should preserve at minimum:
- title
- url
- snippet or raw content
- quality score if evaluated
- extraction result if processed

Do not invent citations.
Do not claim a source supports something unless it actually does.

---

## Multimodal Rules

If user provides:
- text only -> run text pipeline
- text + image -> run text pipeline and vision analysis, then merge results
- audio -> prefer transcription-first workflow unless repository explicitly supports direct audio reasoning

For images:
- extract only what is reasonably visible
- distinguish OCR-like extraction from interpretation
- avoid overclaiming when image quality is low

---

## Project Structure Guidance

Prefer a structure close to:

- `app/`
  - `agents/`
  - `tools/`
  - `prompts/`
  - `schemas/`
  - `graph.py`
  - `state.py`
  - `config.py`
  - `main.py`
- `tests/`
- `docs/`
- `examples/`

Keep responsibilities separated:
- agents decide and transform
- tools access external systems
- prompts store prompt templates
- schemas define structured outputs
- graph/orchestrator wires the workflow

---

## Coding Standards

Use Python unless the task clearly requires another language.

Python rules:
- use type hints
- prefer dataclasses or pydantic models for structured data
- write small functions
- document non-obvious decisions
- fail loudly and clearly
- log meaningful steps
- avoid broad bare `except`
- keep side effects localized

When returning dictionaries, keep keys stable across the codebase.

Prefer:
- explicit names
- simple control flow
- one concern per function
- reusable helper utilities

Avoid:
- unnecessary classes
- premature optimization
- fragile regex-heavy parsing when structured parsing is possible

---

## Prompt Engineering Rules

Prompt files should be stored centrally, not inline everywhere.

Prompts should:
- define role clearly
- specify output schema explicitly
- request concise reasoning where helpful
- forbid non-JSON output when structured parsing is required

Do not make prompts overly long unless necessary.
Prefer stable schemas over clever prose.

When JSON output is required:
- clearly specify exact keys
- instruct the model to return only valid JSON
- validate outputs in code

---

## Testing Expectations

Whenever changing core workflow code:
- add or update tests
- test at least one happy path
- test one failure or degraded-input path
- test structured output shape when possible

Important test targets:
- state transitions
- source filtering behavior
- JSON parsing robustness
- fallback behavior when a model returns malformed output
- vision path only when image input exists

Prefer fast unit tests before heavier integration tests.

---

## Error Handling

Do not silently swallow failures.

If an external call fails:
- return a clear error object or fallback state
- preserve enough detail for debugging
- keep the pipeline recoverable when reasonable

Examples:
- search failure
- page extraction failure
- malformed model JSON
- missing image file
- Ollama connection error

Use graceful degradation where possible:
- skip one broken source instead of crashing the entire run
- but do not hide the fact that a skip happened

---

## Performance Rules

Default to a practical MVP.

Before adding complexity:
- make the end-to-end pipeline work
- keep the number of model calls reasonable
- avoid duplicate page fetches
- deduplicate similar sources before expensive processing

Only add caching, memory, or concurrency when it clearly improves the workflow.

---

## Memory / Retrieval Rules

If retrieval or long-term memory is added:
- use `nomic-embed-text:latest` for embeddings unless changed intentionally
- keep raw documents separate from derived chunks
- preserve source provenance
- document chunking assumptions
- never treat retrieval results as automatically true

---

## Documentation Rules

When adding features, update docs if behavior changes.

Prefer:
- short README guidance
- architecture notes in `docs/architecture.md`
- prompt/schema notes in `docs/`
- examples in `examples/`

If `AGENTS.md` becomes too large, keep it concise and move details into `docs/`, since Codex guidance works best when the main AGENTS file stays short and points to deeper sources of truth. :contentReference[oaicite:1]{index=1}

---

## How Codex Should Work In This Repo

Before making changes:
1. inspect project structure
2. identify the relevant agent/tool/schema files
3. propose the smallest coherent change
4. preserve existing architecture unless clearly broken
5. run relevant tests if available

When implementing a new feature:
1. define or update schema first
2. update agent logic
3. wire into graph/orchestrator
4. add tests
5. update docs if needed

When fixing bugs:
1. locate failing stage
2. identify whether the bug is in tool, prompt, parsing, state, or orchestration
3. patch minimally
4. verify with focused tests

---

## PR / Change Quality Bar

A change is not complete unless it:
- fits the architecture
- keeps outputs understandable
- preserves or improves reliability
- avoids unnecessary complexity
- includes tests or a clear reason tests were not added
- does not break source traceability

---

## Good Defaults for This Repo

Assume:
- local inference through Ollama
- text model = `qwen3:8b`
- vision model = `llama3.2-vision:latest`
- embeddings model = `nomic-embed-text:latest`

If another model is introduced, document why.

---

## Non-Goals

Do not turn this project into:
- a generic chat app
- an over-complicated autonomous agent swarm
- a UI-first project before the backend works
- an unstructured “search then dump text” tool

This project is a research workflow system.



# AGENTS.md

## Project
Multi-Agent Research Assistant

This repository implements a multi-agent research system that:
- accepts a user research query
- searches and collects web information
- filters unreliable sources
- extracts structured insights
- optionally analyzes user-provided images
- synthesizes a decision-ready report

Primary goal:
Build a reliable, explainable research workflow rather than a generic chatbot.

---

## Core Architecture

Main workflow:
1. Research Agent
2. Critic Agent
3. Summarizer Agent
4. Vision Agent (optional)
5. Synthesizer Agent
6. Orchestrator (LangGraph)

System principles:
- structured outputs
- explicit source handling
- deterministic pipelines where possible
- modular and testable components
- minimal hidden behavior

---

## Mandatory Technology Stack

### LangChain (REQUIRED)
Role:
- agent development
- tool definition
- reasoning chains
- LLM interaction layer

Used for:
- implementing all agents
- chaining logic
- tool calling

---

### LlamaIndex (REQUIRED)
Role:
- indexing private data
- RAG pipeline
- query engine for contextual retrieval

Used for:
- document ingestion
- chunking
- retrieval over private data
- contextual augmentation

---

### LLM Provider (REQUIRED)

Default provider:
- Ollama (local inference)

Allowed alternatives:
- OpenAI API
- Anthropic API
- Groq

Rules:
- provider must be configurable
- do not hardcode provider logic

---

### Python (REQUIRED)

Role:
- main backend language

Rules:
- all core logic must be implemented in Python
- orchestration, agents, tools, and RAG pipeline must remain in Python

---

### Vector Store (REQUIRED)

Supported:
- ChromaDB (default)

Role:
- store embeddings
- enable retrieval
- support RAG

Rules:
- preserve metadata
- maintain source traceability
- retrieval results must not be treated as guaranteed truth

---

## Model Policy

Text model:
- `qwen3:8b` (via Ollama)

Vision model:
- `llama3.2-vision:latest`

Embeddings:
- `nomic-embed-text:latest`

Usage rules:

Use `qwen3:8b` for:
- reasoning
- source evaluation
- structured extraction
- report synthesis

Use `llama3.2-vision` ONLY for:
- image analysis
- charts
- screenshots
- OCR-like extraction

Do NOT:
- use vision models for text tasks
- use coding models (e.g. codellama) for research logic

---

## External APIs and Tools

### Search API
Primary:
- Tavily API

Responsibilities:
- retrieve web sources
- return title, URL, snippet

Rules:
- limit results (5–10)
- normalize outputs before processing
- do not switch provider silently

Optional (not default):
- SerpAPI
- GDELT

---

### Content Extraction
Primary:
- Jina Reader (`r.jina.ai`)

Responsibilities:
- convert URLs into clean text
- prepare content for LLM processing

Rules:
- truncate large pages
- handle extraction failures gracefully
- do not build custom scrapers unless necessary

---

### Audio Handling

Preferred workflow:
1. transcribe audio
2. process as text

Direct audio reasoning:
- only if explicitly supported

---

## Agent Responsibilities

### Research Agent
Input:
- query

Output:
- structured sources

Responsibilities:
- call Tavily
- normalize results

Schema:
```json
{
  "title": "...",
  "url": "...",
  "content": "..."
}