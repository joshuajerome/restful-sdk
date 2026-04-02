"""Execute workflows — full run or individual stages."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from restful.workflow.context import WorkflowContext
from restful.workflow.decorator import StageInfo
from restful.workflow.loader import load_workflow

logger = logging.getLogger(__name__)


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

        # Persist variables after run
        if self.ctx._variables is not None:
            self.ctx._variables.save()

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
