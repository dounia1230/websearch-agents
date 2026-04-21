from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.config import AppConfig
from app.llm.factory import build_text_model, build_vision_model
from app.utils.json_utils import parse_json_response

StructuredModelT = TypeVar("StructuredModelT", bound=BaseModel)


def invoke_structured_model(
    *,
    config: AppConfig,
    schema: type[StructuredModelT],
    system_prompt: str,
    user_input: str,
    image_paths: list[str] | None = None,
) -> StructuredModelT:
    llm = build_vision_model(config) if image_paths else build_text_model(config)
    prompt_with_schema = _attach_schema_instructions(system_prompt, schema)

    if image_paths:
        response = llm.invoke(
            [
                SystemMessage(content=prompt_with_schema),
                HumanMessage(content=[{"type": "text", "text": user_input}, *_build_image_blocks(image_paths)]),
            ]
        )
    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                ("human", "{user_input}"),
            ]
        )
        response = (prompt | llm).invoke({"system_prompt": prompt_with_schema, "user_input": user_input})

    response_text = getattr(response, "text", None)
    if isinstance(response_text, str) and response_text.strip():
        content = response_text.strip()
    else:
        content = _extract_text_content(response.content)
    return parse_json_response(content, schema)


def _attach_schema_instructions(system_prompt: str, schema: type[StructuredModelT]) -> str:
    schema_json = json.dumps(schema.model_json_schema(), indent=2)
    return "\n\n".join(
        [
            system_prompt.strip(),
            "Return only valid JSON.",
            "Use exactly the following JSON schema:",
            schema_json,
        ]
    )


def _extract_text_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                text_value = block.get("text")
                if isinstance(text_value, str):
                    text_parts.append(text_value)
        if text_parts:
            return "\n".join(part.strip() for part in text_parts if part.strip())

    raise ValueError(f"Could not extract text from model response content: {content!r}")


def _build_image_blocks(image_paths: list[str]) -> list[dict[str, str]]:
    image_blocks: list[dict[str, str]] = []
    for image_path in image_paths:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file was not found: {path}")
        mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
        image_blocks.append(
            {
                "type": "image",
                "base64": base64.b64encode(path.read_bytes()).decode("utf-8"),
                "mime_type": mime_type,
            }
        )
    return image_blocks
