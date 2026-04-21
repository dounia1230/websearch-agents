from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError


JsonModelT = TypeVar("JsonModelT", bound=BaseModel)

CODE_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_object(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        raise ValueError("Model returned an empty response.")

    code_block_match = CODE_BLOCK_PATTERN.search(stripped)
    if code_block_match:
        stripped = code_block_match.group(1).strip()

    for opener, closer in (("{", "}"), ("[", "]")):
        start_index = stripped.find(opener)
        end_index = stripped.rfind(closer)
        if start_index != -1 and end_index != -1 and end_index > start_index:
            return stripped[start_index : end_index + 1]

    return stripped


def parse_json_response(text: str, schema: type[JsonModelT]) -> JsonModelT:
    candidates = _build_candidates(text)
    errors: list[str] = []

    for candidate in candidates:
        try:
            return schema.model_validate_json(candidate)
        except (ValidationError, json.JSONDecodeError, ValueError) as exc:
            errors.append(str(exc))
            try:
                return schema.model_validate(json.loads(candidate))
            except (ValidationError, json.JSONDecodeError, TypeError, ValueError) as nested_exc:
                errors.append(str(nested_exc))

    joined_errors = "; ".join(errors[-4:]) if errors else "No parse attempts succeeded."
    raise ValueError(f"Could not parse {schema.__name__} from model response. {joined_errors}")


def _build_candidates(text: str) -> list[str]:
    stripped = text.strip()
    candidates = [stripped]
    extracted = extract_json_object(stripped)
    if extracted != stripped:
        candidates.append(extracted)

    unique_candidates: list[str] = []
    for candidate in candidates:
        normalized = candidate.strip()
        if normalized and normalized not in unique_candidates:
            unique_candidates.append(normalized)
    return unique_candidates
