from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class AuthStrategy(Protocol):
    """Protocol for auth strategies. Client calls these to get headers."""

    def auth_headers(self) -> Mapping[str, str]:
        """Return headers to attach to every request."""
        ...

    def invalidate(self) -> None:
        """Clear cached credentials, forcing re-auth on next call."""
        ...
