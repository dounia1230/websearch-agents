from __future__ import annotations

import logging
from pathlib import Path

from app.config import AppConfig
from app.schemas import PipelineIssue, SourceRecord

logger = logging.getLogger(__name__)

SUPPORTED_PRIVATE_EXTENSIONS = [".md", ".txt", ".pdf", ".docx"]


def retrieve_private_context(question: str, config: AppConfig) -> tuple[list[SourceRecord], list[PipelineIssue]]:
    if config.private_data_dir is None:
        return [], []
    if not config.private_data_dir.exists():
        return [], [
            PipelineIssue(
                stage="retrieval",
                message=f"Configured PRIVATE_DATA_DIR does not exist: {config.private_data_dir}",
                recoverable=True,
            )
        ]

    try:
        documents = _load_documents(config.private_data_dir)
        if not documents:
            return [], []
        nodes = _retrieve_nodes(question, config, documents)
    except Exception as exc:
        logger.exception("Private retrieval failed.")
        return [], [
            PipelineIssue(
                stage="retrieval",
                message=f"Private retrieval failed: {exc}",
                recoverable=True,
            )
        ]

    sources: list[SourceRecord] = []
    for index, node in enumerate(nodes, start=1):
        metadata = dict(getattr(node, "metadata", {}) or {})
        text = getattr(node, "text", "") or ""
        title = str(metadata.get("file_name") or metadata.get("file_path") or f"Private document {index}")
        file_path = metadata.get("file_path") or title
        sources.append(
            SourceRecord(
                id=f"P{index}",
                title=Path(str(title)).name,
                url=f"file://{file_path}",
                snippet=_truncate(text, 400),
                raw_content="",
                extracted_content=_truncate(text, config.max_reader_content_chars),
                source_type="private_data",
                search_score=None,
                metadata={"file_path": file_path, **metadata},
            )
        )
    return sources, []


def _load_documents(private_data_dir: Path):
    from llama_index.core import SimpleDirectoryReader

    reader = SimpleDirectoryReader(
        input_dir=str(private_data_dir),
        recursive=True,
        required_exts=SUPPORTED_PRIVATE_EXTENSIONS,
    )
    return reader.load_data()


def _retrieve_nodes(question: str, config: AppConfig, documents):
    import chromadb
    from llama_index.core import StorageContext, VectorStoreIndex
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore

    if config.chroma_persist_dir is not None:
        client = chromadb.PersistentClient(path=str(config.chroma_persist_dir))
    else:
        client = chromadb.EphemeralClient()

    try:
        client.delete_collection(config.chroma_collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(config.chroma_collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = OllamaEmbedding(
        model_name=config.embedding_model,
        base_url=config.ollama_base_url,
    )
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    retriever = index.as_retriever(similarity_top_k=config.retrieval_top_k)
    return retriever.retrieve(question)


def _truncate(text: str, limit: int) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[:limit].rstrip()}..."
