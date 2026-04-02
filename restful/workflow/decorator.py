"""@stage decorator — registers functions as named workflow stages."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class StageInfo:
    name: str
    func: Callable
    order: int


# Global registry — populated when a workflow module is imported
_registry: list[StageInfo] = []


def stage(name: str) -> Callable:
    """
    Decorator that registers a function as a named workflow stage.

    Usage:
        @stage("Get Blueprint Catalog")
        def get_blueprints(ctx):
            ...

    The function works with or without the decorator — @stage just adds
    metadata for the CLI and GUI to discover and run stages individually.
    """

    def wrapper(func: Callable) -> Callable:
        _registry.append(StageInfo(name=name, func=func, order=len(_registry)))
        func._stage_name = name  # type: ignore[attr-defined]
        func._stage_order = len(_registry) - 1  # type: ignore[attr-defined]
        return func

    return wrapper


def get_registry() -> list[StageInfo]:
    """Return the current stage registry."""
    return list(_registry)


def clear_registry() -> None:
    """Clear the registry. Called before importing a new workflow module."""
    _registry.clear()
