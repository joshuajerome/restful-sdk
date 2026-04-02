from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Endpoint:
    """A typed REST endpoint constant. Used at runtime in workflow scripts."""

    path: str
    methods: tuple[str, ...]


@dataclass
class EndpointSpec:
    """
    Normalized endpoint definition produced by an adapter during ingestion.
    This is the intermediate format between source parsing and code generation.
    """

    path: str
    methods: tuple[str, ...]
    name: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
