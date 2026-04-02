"""Plugin registry — discovers adapters from plugin directories."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import yaml

from restful.plugins.base import Adapter


_registry: dict[str, Any] = {}


def load_plugin(plugin_dir: Path) -> Any:
    """Load a plugin from a directory containing plugin.yaml + adapter.py.

    Returns the adapter module (must have `name: str` and `parse(source) -> list[EndpointSpec]`).
    """
    plugin_dir = Path(plugin_dir)

    manifest_path = plugin_dir / "plugin.yaml"
    adapter_path = plugin_dir / "adapter.py"

    if not plugin_dir.is_dir():
        raise FileNotFoundError(f"Plugin directory not found: {plugin_dir}")
    if not adapter_path.exists():
        raise FileNotFoundError(f"No adapter.py in plugin directory: {plugin_dir}")

    # Load manifest if present (optional but recommended)
    manifest: dict = {}
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}

    # Load adapter module
    spec = importlib.util.spec_from_file_location(
        f"_plugin_{plugin_dir.name}", adapter_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load adapter from {adapter_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Validate adapter has required interface
    if not hasattr(mod, "parse"):
        raise AttributeError(f"adapter.py missing parse() function in {plugin_dir}")
    if not hasattr(mod, "name"):
        # Fall back to manifest name or directory name
        mod.name = manifest.get("name", plugin_dir.name)

    # Register it
    _registry[mod.name] = mod
    return mod


def register(adapter: Adapter) -> None:
    """Register an adapter manually."""
    _registry[adapter.name] = adapter


def get(name: str) -> Any | None:
    """Get a registered adapter by name."""
    return _registry.get(name)


def list_plugins() -> list[str]:
    """List all registered plugin names."""
    return sorted(_registry.keys())


def get_manifest(plugin_dir: Path) -> dict:
    """Read plugin.yaml manifest from a plugin directory."""
    manifest_path = Path(plugin_dir) / "plugin.yaml"
    if not manifest_path.exists():
        return {"name": Path(plugin_dir).name}
    with manifest_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
