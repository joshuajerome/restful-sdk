from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_REQUIRED_FIELDS = ("plugin", "source", "endpoints")


@dataclass
class PostItConfig:
    project: str
    plugin: str
    source: str
    endpoints: str
    base_url: str = ""
    plugin_path: str = ""

    @classmethod
    def load(cls, path: Path = Path("restful.yaml")) -> PostItConfig:
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Config must be a YAML mapping, got {type(data).__name__}")

        missing = [f for f in _REQUIRED_FIELDS if f not in data]
        if missing:
            raise ValueError(f"Config missing required fields: {', '.join(missing)}")

        return cls(
            project=data.get("project", ""),
            plugin=data["plugin"],
            source=data["source"],
            endpoints=data["endpoints"],
            base_url=data.get("base_url", ""),
            plugin_path=data.get("plugin_path", ""),
        )
