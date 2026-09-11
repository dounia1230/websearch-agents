# Architecture

## Workflow

The graph executes the following stages:

1. `planner`
2. `research`
3. `critic`
4. `summarize`
5. `vision` when `image_paths` exist
6. `synthesize`

The `critic` node can route back to `planner` while the retry budget remains.

## Agent Responsibilities

`planner_agent`

- interprets the user's actual intent
- generates 3 to 5 focused search queries
- defines include/exclude retrieval cues
- emits a typed `PlannerOutput`

`research_agent`

- uses the planner output to drive multi-query Tavily search
- enriches top web results with Jina Reader
- optionally retrieves local/private evidence through LlamaIndex + ChromaDB
- applies deterministic source-quality and initial intent-alignment heuristics
- emits a typed `ResearchBrief`

`critic_agent`

- checks evidence sufficiency
- scores sources on authority, relevance to intent, specificity, recency, evidence, and clarity
- rejects broad, tangential, or wrong-context sources before summarization
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
