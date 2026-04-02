"""Find the workspace root by looking for *.config.yaml."""

from __future__ import annotations

from pathlib import Path

from restful.workspace.config import WorkspaceConfig


def find_workspace_root(start: Path | None = None) -> Path:
    """Walk up from start (default: cwd) until a *.config.yaml is found. Returns the directory."""
    current = (start or Path.cwd()).resolve()
    while True:
        configs = list(current.glob("*.config.yaml"))
        if configs:
            return current
        parent = current.parent
        if parent == current:
            raise FileNotFoundError("No workspace found (no *.config.yaml in any parent directory)")
        current = parent


def find_config_file(start: Path | None = None) -> Path:
    """Find the *.config.yaml file in the workspace root."""
    root = find_workspace_root(start)
    configs = list(root.glob("*.config.yaml"))
    if not configs:
        raise FileNotFoundError(f"No *.config.yaml found in {root}")
    if len(configs) > 1:
        raise ValueError(f"Multiple config files found in {root}: {[c.name for c in configs]}")
    return configs[0]


def load_workspace(start: Path | None = None) -> WorkspaceConfig:
    """Discover and load the workspace config from cwd or a given path."""
    config_path = find_config_file(start)
    return WorkspaceConfig.load(config_path)
