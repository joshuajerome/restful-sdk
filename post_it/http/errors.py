from __future__ import annotations


class HttpError(RuntimeError):
    def __init__(
        self,
        *,
        method: str,
        url: str,
        status_code: int,
        body: str,
    ):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.body = body
        super().__init__(f"{method} {url} -> {status_code}: {body[:300]}")
