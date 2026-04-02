from __future__ import annotations

import logging
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
    REST client with typed endpoints, auth injection, and 401 retry.

    Usage:
        from restful import Client, BearerAuth

        client = Client(
            base_url="https://100.94.115.90",
            auth=BearerAuth(
                base_url="https://100.94.115.90",
                login_path="/security/v1/auth/login",
                payload={"username": "admin", "password": "secret"},
            ),
        )

        resp = client.get(ep.BlueprintTemplates)
    """

    def __init__(
        self,
        base_url: str,
        auth: AuthStrategy | None = None,
        verify_tls: bool = False,
        timeout_s: int = 15,
    ):
        self.base_url = base_url
        self.auth = auth
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
        """Execute a request with 401 retry."""
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

        try:
            return _do()
        except HttpError as e:
            if e.status_code == 401 and self.auth:
                logger.warning("401 received; re-authenticating and retrying")
                self.auth.invalidate()
                self._apply_auth()
                return _do()
            raise

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
