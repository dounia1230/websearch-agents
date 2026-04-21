from __future__ import annotations

from pydantic import BaseModel

from app.utils.json_utils import parse_json_response


class DemoSchema(BaseModel):
    name: str
    count: int


def test_parse_json_response_extracts_json_from_code_fence() -> None:
    raw_response = """
    Here is the result:

    ```json
    {
      "name": "alpha",
      "count": 3
    }
    ```
    """

    parsed = parse_json_response(raw_response, DemoSchema)

    assert parsed.name == "alpha"
    assert parsed.count == 3


def test_parse_json_response_raises_on_invalid_payload() -> None:
    try:
        parse_json_response("not valid json", DemoSchema)
    except ValueError as exc:
        assert "Could not parse DemoSchema" in str(exc)
    else:
        raise AssertionError("Expected parse_json_response to raise ValueError for invalid payload.")
