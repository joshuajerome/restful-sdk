from __future__ import annotations

from pathlib import Path
from typing import Protocol

from post_it.models import EndpointSpec


class Adapter(Protocol):
    """Protocol for endpoint ingestion adapters."""

    name: str

    def parse(self, source: Path) -> list[EndpointSpec]:
        """Parse a source file and return normalized endpoint specs."""
        ...
