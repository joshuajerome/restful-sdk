"""Load a workflow Python file and read its registered stages."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from restful.workflow.decorator import StageInfo, clear_registry, get_registry


def load_workflow(workflow_path: Path) -> list[StageInfo]:
    """
    Import a workflow .py file and return its registered @stage functions.

    Clears the global stage registry before import, then collects all
    @stage-decorated functions that were registered during import.
    """
    path = workflow_path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Workflow not found: {path}")
    if not path.suffix == ".py":
        raise ValueError(f"Workflow must be a .py file: {path}")

    # Clear previous registrations
    clear_registry()

    # Add the workflow's parent to sys.path so relative imports work
    parent = str(path.parent)
    added_to_path = parent not in sys.path
    if added_to_path:
        sys.path.insert(0, parent)

    try:
        module_name = f"_workflow_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load workflow: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        if added_to_path and parent in sys.path:
            sys.path.remove(parent)

    return get_registry()
