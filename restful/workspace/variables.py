"""File-backed workspace variable store (.restful/variables.json)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class VariableStore:
    """Key-value variable store persisted to disk."""

    def __init__(self, workspace_root: Path):
        self._dir = workspace_root / ".restful"
        self._path = self._dir / "variables.json"
        self._data: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                with self._path.open("r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        os.replace(tmp, self._path)

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = str(value) if not isinstance(value, str) else value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def all(self) -> dict[str, str]:
        return dict(self._data)

    def save(self) -> None:
        """Persist current state to disk."""
        self._save()

    def __repr__(self) -> str:
        return f"VariableStore({len(self._data)} vars)"
