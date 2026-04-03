from __future__ import annotations

import base64
import json
import logging
import time
from collections.abc import Mapping
from typing import Any

import requests

from restful.auth.cache import TokenCache
from restful.http.errors import HttpError

logger = logging.getLogger(__name__)


def _jwt_exp_epoch(token: str) -> int | None:
    """Extract exp (epoch seconds) from a JWT without verifying signature."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        pad = "=" * (-len(payload_b64) % 4)
        payload = base64.urlsafe_b64decode(payload_b64 + pad).decode("utf-8", errors="ignore")
        data = json.loads(payload)
        exp = data.get("exp")
        return int(exp) if exp else None
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


class BearerAuth:
    """
    Bearer token auth strategy with caching and auto-refresh.

    Usage:
        auth = BearerAuth(
            base_url="https://100.94.115.90",
            login_path="/security/v1/auth/login",
            payload={"username": "admin", "password": "secret"},
            token_key="access_token",
        )

    The token is fetched lazily on first use, cached to .restful/cache.json,
    and auto-refreshed when nearing expiry.
    """

    def __init__(
        self,
        base_url: str,
        login_path: str,
        payload: dict[str, Any],
        token_key: str = "access_token",
        cache: TokenCache | None = None,
        refresh_skew_s: int = 60,
        verify_tls: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.login_path = login_path
        self.payload = payload
        self.token_key = token_key
        self.cache = cache or TokenCache()
        self.refresh_skew_s = refresh_skew_s
        self.verify_tls = verify_tls

        self._token: str | None = None
        self._expires_at: int | None = None

    @property
    def _cache_key(self) -> str:
        return self.base_url

    def _login(self) -> dict[str, Any]:
        """POST to the login endpoint and return the response body."""
        url = self.base_url + self.login_path
        logger.debug("Authenticating to %s", url)
        r = requests.post(
            url,
            json=self.payload,
            verify=self.verify_tls,
            timeout=15,
            headers={"Accept": "application/json"},
        )
        if r.status_code not in (200, 201):
            raise HttpError(method="POST", url=url, status_code=r.status_code, body=r.text)
        return r.json()

    def _load_from_cache(self) -> bool:
        token = self.cache.load(self._cache_key)
        if not token:
            return False
        self._token = token
        logger.info("Reused cached token for %s", self.base_url)
        return True

    def _refresh(self) -> None:
        data = self._login()
        # Try configured key first, then common fallbacks
        token = data.get(self.token_key)
        if not token:
            for fallback in ("access_token", "token", "jwt", "id_token"):
                token = data.get(fallback)
                if token:
                    break
        if not token:
            keys = list(data.keys())
            raise RuntimeError(f"Login response missing token (tried '{self.token_key}' + fallbacks). Keys: {keys}")

        exp = _jwt_exp_epoch(token)
        if not exp and "expires_in" in data:
            exp = int(time.time()) + int(data["expires_in"])

        self._token = token
        self._expires_at = exp
        self.cache.save(self._cache_key, token, exp)
        logger.info("Token refreshed and cached for %s", self.base_url)

    def auth_headers(self) -> Mapping[str, str]:
        if not self._token:
            if not self._load_from_cache():
                self._refresh()
        elif self._expires_at and time.time() >= (self._expires_at - self.refresh_skew_s):
            logger.info("Token nearing expiry; refreshing")
            self._refresh()
        return {"Authorization": f"Bearer {self._token}"}

    def invalidate(self) -> None:
        self._token = None
        self._expires_at = None
