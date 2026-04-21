# Architecture

## Workflow

The graph executes the following stages:

1. `research`
2. `critic`
3. `summarize`
4. `vision` when `image_paths` exist
5. `synthesize`

The `critic` node can route back to `research` while the retry budget remains.

## Agent Responsibilities

`research_agent`

- queries Tavily
- enriches top web results with Jina Reader
- optionally retrieves local/private evidence through LlamaIndex + ChromaDB
- applies deterministic source-quality heuristics
- emits a typed `ResearchBrief`

`critic_agent`

- checks evidence sufficiency
- identifies unsupported or weak claims
- proposes targeted follow-up queries
- emits a typed `CritiqueReport`

`summarizer_agent`

- compresses the brief into decision-ready insights
- surfaces opportunities, risks, and limitations
- emits a typed `SummaryReport`

`vision_agent`

- analyzes only user-provided images
- separates visible facts from interpretation
- emits a typed `VisionReport`

`synthesizer_agent`

- merges summary, critique, sources, and optional vision output
- emits the final `FinalReport`

## Source Handling

Every source object preserves:

- `id`
- `title`
- `url`
- `snippet`
- `raw_content`
- `extracted_content`
- `quality_score`
- `quality_label`
- `quality_rationale`
- extraction status metadata

Filtered-out sources are preserved in `candidate_sources`; downstream reasoning uses `selected_sources`.

## Retrieval

When `PRIVATE_DATA_DIR` is configured:

- files are loaded through `SimpleDirectoryReader`
- embeddings are generated with `nomic-embed-text:latest` via Ollama
- ChromaDB is used as the vector store
- retrieved chunks are converted into `private_data` sources with file provenance

## Structured Output

All agent outputs are validated with `pydantic` models. The model wrapper:

- appends JSON schema instructions to prompts
- invokes the configured LangChain chat model
- attempts JSON parsing directly
- falls back to extracting JSON from surrounding prose or fenced code blocks

This keeps the workflow recoverable when a model wraps valid JSON in extra text.
