from __future__ import annotations

from typing import Any

from app.config import AppConfig


def build_text_model(config: AppConfig):
    return _build_chat_model(
        provider=config.llm_provider,
        model_name=config.text_model,
        config=config,
    )


def build_vision_model(config: AppConfig):
    return _build_chat_model(
        provider=config.llm_provider,
        model_name=config.vision_model,
        config=config,
    )


def _build_chat_model(provider: str, model_name: str, config: AppConfig):
    normalized_provider = provider.strip().lower()
    temperature = 0.0
    common_kwargs: dict[str, Any] = {"temperature": temperature}

    if normalized_provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model_name,
            base_url=config.ollama_base_url,
            num_predict=config.max_generation_tokens,
            **common_kwargs,
        )

    if normalized_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_name,
            api_key=config.openai_api_key,
            base_url=config.openai_base_url or None,
            max_tokens=config.max_generation_tokens,
            **common_kwargs,
        )

    if normalized_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=model_name,
            api_key=config.anthropic_api_key,
            max_tokens=config.max_generation_tokens,
            **common_kwargs,
        )

    if normalized_provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model_name,
            api_key=config.groq_api_key,
            max_tokens=config.max_generation_tokens,
            **common_kwargs,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER '{config.llm_provider}'.")
