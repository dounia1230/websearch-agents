from __future__ import annotations

import requests


JINA_READER_PREFIX = "https://r.jina.ai/"


def read_url(url: str, timeout_seconds: int = 20) -> str:
    response = requests.get(
        f"{JINA_READER_PREFIX}{url}",
        headers={"Accept": "text/plain"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return response.text.strip()
