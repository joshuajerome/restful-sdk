from __future__ import annotations

from post_it.plugins.base import Adapter
from post_it.plugins.snf_instance_rest.adapter import SnfInstanceRestAdapter

# Built-in plugins
_BUILTIN: dict[str, Adapter] = {
    "snf-instance-rest": SnfInstanceRestAdapter(),
}

_registry: dict[str, Adapter] = dict(_BUILTIN)


def register(adapter: Adapter) -> None:
    """Register a custom adapter."""
    _registry[adapter.name] = adapter


def get(name: str) -> Adapter | None:
    """Get an adapter by name."""
    return _registry.get(name)


def list_plugins() -> list[str]:
    """List all registered plugin names."""
    return sorted(_registry.keys())
