"""Execute workflows — full run, individual stages, and resume."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from restful.workflow.context import WorkflowContext
from restful.workflow.decorator import StageInfo
from restful.workflow.loader import load_workflow

logger = logging.getLogger(__name__)

LAST_RUN_FILE = ".restful/last_run.json"


@dataclass
class StageResult:
    stage_name: str
    success: bool
    return_value: Any = None
    error: str | None = None
    duration_ms: int = 0
    captured_vars: dict[str, str] | None = None


class WorkflowRunner:
    """Runs workflow stages with a WorkflowContext."""

    def __init__(self, ctx: WorkflowContext):
        self.ctx = ctx

    def run(self, workflow_path: Path) -> list[StageResult]:
        """Load and run all stages in a workflow file."""
        stages = load_workflow(workflow_path)
        if not stages:
            logger.warning("No @stage functions found in %s", workflow_path)
            return []

        results = []
        for stage_info in stages:
            result = self._execute_stage(stage_info)
            results.append(result)
            if not result.success:
                logger.error("Stage '%s' failed: %s", stage_info.name, result.error)
                break

        # Persist variables and last run
        if self.ctx._variables is not None:
            self.ctx._variables.save()
        self._save_last_run(workflow_path, results)

        return results

    def resume(self, workflow_path: Path, from_stage: str | None = None) -> list[StageResult]:
        """Resume a workflow from a specific stage, skipping completed ones.

        If from_stage is None, resumes from the first failed stage in last_run.json.
        """
        stages = load_workflow(workflow_path)
        if not stages:
            return []

        # Determine where to start
        skip_until: str | None = from_stage
        if skip_until is None:
            last = self._load_last_run(workflow_path)
            if last:
                for r in last:
                    if not r.get("success", False):
                        skip_until = r.get("stage_name")
                        break

        # Run stages, skipping completed ones
        results: list[StageResult] = []
        skipping = skip_until is not None
        for stage_info in stages:
            if skipping and stage_info.name != skip_until:
                results.append(StageResult(stage_name=stage_info.name, success=True, duration_ms=0))
                logger.info("Skipping completed stage: %s", stage_info.name)
                continue
            skipping = False

            result = self._execute_stage(stage_info)
            results.append(result)
            if not result.success:
                break

        if self.ctx._variables is not None:
            self.ctx._variables.save()
        self._save_last_run(workflow_path, results)

        return results

    def run_stage(self, workflow_path: Path, stage_name: str) -> StageResult:
        """Load a workflow and run a single stage by name."""
        stages = load_workflow(workflow_path)
        target = None
        for s in stages:
            if s.name == stage_name:
                target = s
                break

        if target is None:
            available = [s.name for s in stages]
            raise ValueError(f"Stage '{stage_name}' not found. Available: {available}")

        result = self._execute_stage(target)

        if self.ctx._variables is not None:
            self.ctx._variables.save()

        return result

    def list_stages(self, workflow_path: Path) -> list[str]:
        """Return the names of all stages in a workflow."""
        stages = load_workflow(workflow_path)
        return [s.name for s in stages]

    def _save_last_run(self, workflow_path: Path, results: list[StageResult]) -> None:
        """Persist last run results to .restful/last_run.json."""
        try:
            ws_root = workflow_path.parent.parent  # notebooks/flow.py → workspace root
            last_run_path = ws_root / LAST_RUN_FILE
            last_run_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "workflow": str(workflow_path.name),
                "timestamp": time.time(),
                "results": [
                    {
                        "stage_name": r.stage_name,
                        "success": r.success,
                        "error": r.error,
                        "duration_ms": r.duration_ms,
                        "captured_vars": r.captured_vars,
                    }
                    for r in results
                ],
            }
            last_run_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug("Could not save last_run.json: %s", e)

    def _load_last_run(self, workflow_path: Path) -> list[dict] | None:
        """Load last run results from .restful/last_run.json."""
        try:
            ws_root = workflow_path.parent.parent
            last_run_path = ws_root / LAST_RUN_FILE
            if not last_run_path.exists():
                return None
            data = json.loads(last_run_path.read_text(encoding="utf-8"))
            if data.get("workflow") == workflow_path.name:
                return data.get("results", [])
            return None
        except Exception:
            return None

    def _execute_stage(self, stage_info: StageInfo) -> StageResult:
        """Execute a single stage function."""
        logger.info("Running stage: %s", stage_info.name)
        vars_before = dict(self.ctx.all_vars())

        start = time.time()
        try:
            return_value = stage_info.func(self.ctx)
            duration_ms = int((time.time() - start) * 1000)

            # Determine which variables were added/changed
            vars_after = self.ctx.all_vars()
            captured = {k: v for k, v in vars_after.items() if vars_before.get(k) != v}

            return StageResult(
                stage_name=stage_info.name,
                success=True,
                return_value=return_value,
                duration_ms=duration_ms,
                captured_vars=captured if captured else None,
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return StageResult(
                stage_name=stage_info.name,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )
