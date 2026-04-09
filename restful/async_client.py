"""Async wrapper around the synchronous Client using asyncio.to_thread."""

from __future__ import annotations

import asyncio
from typing import Any

from restful.auth.base import AuthStrategy
from restful.client import Client
from restful.http.models import HttpResponse
from restful.models import Endpoint

Expected = int | set[int]


class AsyncClient:
    """Async REST client — wraps the synchronous Client via asyncio.to_thread.

    Usage:
        from restful.async_client import AsyncClient

        async def main():
            async with AsyncClient(base_url="https://api.example.com") as client:
                resp = await client.get(Devices)
                data = resp.json()
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
        self._client = Client(
            base_url=base_url,
            auth=auth,
            verify_tls=verify_tls,
            timeout_s=timeout_s,
            retries=retries,
            retry_on=retry_on,
            retry_delay=retry_delay,
        )

    async def get(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        expected_status: Expected = 200,
    ) -> HttpResponse:
        return await asyncio.to_thread(
            self._client.get, endpoint, params=params, query=query, expected_status=expected_status
        )

    async def post(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = {200, 201},
    ) -> HttpResponse:
        return await asyncio.to_thread(
            self._client.post, endpoint, params=params, query=query, payload=payload, expected_status=expected_status
        )

    async def put(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = {200, 201},
    ) -> HttpResponse:
        return await asyncio.to_thread(
            self._client.put, endpoint, params=params, query=query, payload=payload, expected_status=expected_status
        )

    async def delete(
        self,
        endpoint: Endpoint,
        *,
        params: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        payload: Any = None,
        expected_status: Expected = {200, 201, 204},
    ) -> HttpResponse:
        return await asyncio.to_thread(
            self._client.delete, endpoint, params=params, query=query, payload=payload, expected_status=expected_status
        )

    async def close(self) -> None:
        self._client.close()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
