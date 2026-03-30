from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import requests
import urllib3

from post_it.http.errors import HttpError
from post_it.http.models import HttpResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

Expected = int | set[int]


class HttpClient:
    def __init__(
        self,
        base_url: str,
        verify_tls: bool = False,
        timeout_s: int = 15,
    ):
        self.base_url = base_url.rstrip("/")
        self.verify_tls = verify_tls
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        expected_status: Expected = 200,
    ) -> HttpResponse:
        url = self._url(path)
        exp = {expected_status} if isinstance(expected_status, int) else set(expected_status)

        logger.debug("HTTP %s %s", method, url)
        r = self.session.request(
            method=method,
            url=url,
            params=dict(params) if params else None,
            json=json_body,
            timeout=self.timeout_s,
            verify=self.verify_tls,
        )

        resp = HttpResponse.from_requests(r, method=method)
        if resp.status_code not in exp:
            raise HttpError(
                method=method,
                url=resp.url,
                status_code=resp.status_code,
                body=resp.text,
            )

        return resp

    def close(self) -> None:
        self.session.close()
