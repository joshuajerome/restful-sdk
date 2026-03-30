from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class PostItConfig:
    project: str
    plugin: str
    source: str
    endpoints: str
    base_url: str = ""

    @classmethod
    def load(cls, path: Path = Path("post-it.yaml")) -> PostItConfig:
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(
            project=data.get("project", ""),
            plugin=data["plugin"],
            source=data["source"],
            endpoints=data["endpoints"],
            base_url=data.get("base_url", ""),
        )
