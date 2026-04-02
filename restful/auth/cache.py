from __future__ import annotations

import json
import os
import time
from pathlib import Path

DEFAULT_CACHE_DIR = Path.cwd() / ".restful"
DEFAULT_CACHE_FILE = DEFAULT_CACHE_DIR / "cache.json"


class TokenCache:
    """
    File-based token cache, keyed by base_url.

    Structure:
        {
            "https://100.94.115.90": { "token": "eyJ...", "expires_at": 1711500000 },
            "https://10.0.0.2": { "token": "eyJ...", "expires_at": 1711500000 }
        }
    """

    def __init__(self, path: Path = DEFAULT_CACHE_FILE, skew_s: int = 60):
        self.path = path
        self.skew_s = skew_s

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_all(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.path)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def load(self, key: str) -> str | None:
        """Return cached token if still valid, else None."""
        data = self._read_all()
        entry = data.get(key)
        if not entry:
            return None
        expires_at = entry.get("expires_at")
        if expires_at and time.time() >= (expires_at - self.skew_s):
            return None
        return entry.get("token")

    def save(self, key: str, token: str, expires_at: int | None) -> None:
        data = self._read_all()
        data[key] = {"token": token, "expires_at": expires_at}
        self._write_all(data)
