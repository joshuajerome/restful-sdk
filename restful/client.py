from __future__ import annotations

import logging
import random
import time
from typing import Any

from restful.auth.base import AuthStrategy
from restful.http.client import HttpClient
from restful.http.errors import HttpError
from restful.http.models import HttpResponse
from restful.models import Endpoint

logger = logging.getLogger(__name__)

Expected = int | set[int]


class Client:
    """
    REST client with typed endpoints, auth injection, retry, and 401 re-auth.

    Usage:
        from restful import Client, BearerAuth

        client = Client(
            base_url="https://100.94.115.90",
            auth=BearerAuth(
                base_url="https://100.94.115.90",
                login_path="/security/v1/auth/login",
                payload={"username": "admin", "password": "secret"},
            ),
            retries=3,
            retry_on={500, 502, 503, 504},
        )

        resp = client.get(ep.BlueprintTemplates)
    """

    def __init__(
        self,
        base_url: str,
        auth: AuthStrategy | None = None,
        verify_tls: bool = False,
        timeout_s: int = 15,
        retries: int = 0,
        retry_on: set[int] | None = None,
        retry_delay: float = 1.0,
    ):
        self.base_url = base_url
        self.auth = auth
        self.retries = retries
        self.retry_on = retry_on or {500, 502, 503, 504}
        self.retry_delay = retry_delay
        self.http = HttpClient(
            base_url=base_url,
            verify_tls=verify_tls,
            timeout_s=timeout_s,
        )

    def _resolve_path(self, endpoint: Endpoint, params: dict[str, str] | None) -> str:
        """Build the full path, appending OData key predicates if params given."""
        path = endpoint.path
        if params:
            from urllib.parse import quote

            values = ",".join(quote(str(v), safe="") for v in params.values())
            path = f"{path}({values})"
        return path

    def _apply_auth(self) -> None:
        """Inject current auth headers into the session."""
        if self.auth:
            headers = dict(self.auth.auth_headers())
            self.http.session.headers.update(headers)

    def _call(
        self,
        method: str,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = 200,
    ) -> HttpResponse:
        """Execute a request with retry (exponential backoff) and 401 re-auth."""
        path = self._resolve_path(endpoint, params)
        self._apply_auth()

        def _do() -> HttpResponse:
            return self.http.request(
                method,
                path,
                params=query,
                json_body=payload,
                expected_status=expected_status,
            )

        last_error: HttpError | None = None
        attempts = 1 + self.retries  # 1 initial + N retries

        for attempt in range(attempts):
            try:
                return _do()
            except HttpError as e:
                last_error = e

                # 401 → re-authenticate and retry once (separate from general retry)
                if e.status_code == 401 and self.auth:
                    logger.warning("401 received; re-authenticating and retrying")
                    self.auth.invalidate()
                    self._apply_auth()
                    try:
                        return _do()
                    except HttpError:
                        raise

                # General retry for configured status codes
                if e.status_code in self.retry_on and attempt < attempts - 1:
                    delay = self.retry_delay * (2**attempt) + random.uniform(0, 0.5)
                    logger.warning(
                        "Retry %d/%d after %s %d (waiting %.1fs)",
                        attempt + 1,
                        self.retries,
                        method,
                        e.status_code,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                raise

        if last_error:
            raise last_error
        raise RuntimeError("Unexpected: no response and no error")

    def get(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        expected_status: Expected = 200,
    ) -> HttpResponse:
        return self._call("GET", endpoint, params=params, query=query, expected_status=expected_status)

    def post(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = {200, 201},
    ) -> HttpResponse:
        return self._call(
            "POST", endpoint, params=params, query=query, payload=payload, expected_status=expected_status
        )

    def put(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = {200, 201},
    ) -> HttpResponse:
        return self._call("PUT", endpoint, params=params, query=query, payload=payload, expected_status=expected_status)

    def delete(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = {200, 201, 204},
    ) -> HttpResponse:
        return self._call(
            "DELETE", endpoint, params=params, query=query, payload=payload, expected_status=expected_status
        )

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
