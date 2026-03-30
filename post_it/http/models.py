from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    method: str
    url: str
    headers: dict[str, str]
    text: str

    def json(self) -> Any:
        return json.loads(self.text)

    def __str__(self) -> str:
        path = urlparse(self.url).path
        line = f"{self.method} {self.status_code} {path}"
        try:
            body = json.dumps(self.json(), indent=2)
        except (json.JSONDecodeError, ValueError):
            body = self.text
        return f"{line}\n{body}"

    @classmethod
    def from_requests(cls, r: requests.Response, *, method: str) -> HttpResponse:
        status_code: int = r.status_code if r.status_code is not None else 0
        url: str = r.url if r.url is not None else ""
        return cls(
            status_code=status_code,
            method=method,
            url=url,
            headers=dict(r.headers),
            text=r.text or "",
        )
