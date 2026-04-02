"""Tests for workflow decorator, loader, and runner."""

import pytest

from restful.workflow.context import ClientNamespace, WorkflowContext
from restful.workflow.decorator import clear_registry, get_registry, stage
from restful.workflow.loader import load_workflow
from restful.workflow.runner import WorkflowRunner
from restful.workspace.variables import VariableStore

# ─── Decorator ───────────────────────────────────────────────────────────


def test_stage_decorator_registers():
    clear_registry()

    @stage("Test Stage")
    def my_stage(ctx):
        pass

    reg = get_registry()
    assert len(reg) == 1
    assert reg[0].name == "Test Stage"
    assert reg[0].func is my_stage

    # Cleanup
    clear_registry()


def test_stage_decorator_preserves_function():
    clear_registry()

    @stage("Preserved")
    def my_func(ctx):
        return 42

    assert my_func(None) == 42
    assert my_func._stage_name == "Preserved"  # type: ignore[attr-defined]
    clear_registry()


# ─── Context ─────────────────────────────────────────────────────────────


def test_context_get_set(tmp_path):
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    ctx.set("key", "value")
    assert ctx.get("key") == "value"


def test_context_all_vars(tmp_path):
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    ctx.set("a", "1")
    ctx.set("b", "2")
    assert ctx.all_vars() == {"a": "1", "b": "2"}


def test_context_no_variables_raises():
    ctx = WorkflowContext()
    with pytest.raises(RuntimeError, match="No variable store"):
        ctx.set("key", "value")


def test_client_namespace():
    from unittest.mock import MagicMock

    ns = ClientNamespace()
    mock_client = MagicMock()
    ns._add("sfm", mock_client)
    assert ns.sfm is mock_client


def test_client_namespace_missing():
    ns = ClientNamespace()
    with pytest.raises(AttributeError, match="No API client 'missing'"):
        ns.missing  # noqa: B018


# ─── Loader ──────────────────────────────────────────────────────────────


def test_load_workflow_from_file(tmp_path):
    wf = tmp_path / "test_wf.py"
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("Step One")
def step_one(ctx):
    ctx.set("result", "done")
    return "ok"

@stage("Step Two")
def step_two(ctx):
    return ctx.get("result")
"""
    )
    stages = load_workflow(wf)
    assert len(stages) == 2
    assert stages[0].name == "Step One"
    assert stages[1].name == "Step Two"


def test_load_workflow_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_workflow(tmp_path / "nonexistent.py")


def test_load_workflow_not_py(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    with pytest.raises(ValueError, match=".py"):
        load_workflow(f)


# ─── Runner ──────────────────────────────────────────────────────────────


def test_runner_executes_all_stages(tmp_path):
    wf = tmp_path / "workflows" / "chain.py"
    wf.parent.mkdir(parents=True)
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("Set Value")
def set_val(ctx):
    ctx.set("x", "42")

@stage("Read Value")
def read_val(ctx):
    return ctx.get("x")
"""
    )
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    runner = WorkflowRunner(ctx)
    results = runner.run(wf)

    assert len(results) == 2
    assert results[0].success
    assert results[0].captured_vars == {"x": "42"}
    assert results[1].success
    assert results[1].return_value == "42"


def test_runner_single_stage(tmp_path):
    wf = tmp_path / "single.py"
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("Alpha")
def alpha(ctx):
    ctx.set("a", "1")

@stage("Beta")
def beta(ctx):
    ctx.set("b", "2")
"""
    )
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    runner = WorkflowRunner(ctx)
    result = runner.run_stage(wf, "Beta")

    assert result.success
    assert result.stage_name == "Beta"
    assert vs.get("b") == "2"
    assert vs.get("a") is None  # Alpha was not run


def test_runner_stage_not_found(tmp_path):
    wf = tmp_path / "empty.py"
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("Only")
def only(ctx):
    pass
"""
    )
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    runner = WorkflowRunner(ctx)

    with pytest.raises(ValueError, match="not found"):
        runner.run_stage(wf, "Missing Stage")


def test_runner_handles_stage_error(tmp_path):
    wf = tmp_path / "error.py"
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("Fail")
def fail_stage(ctx):
    raise RuntimeError("Intentional error")
"""
    )
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    runner = WorkflowRunner(ctx)
    results = runner.run(wf)

    assert len(results) == 1
    assert not results[0].success
    assert "Intentional error" in results[0].error


def test_runner_list_stages(tmp_path):
    wf = tmp_path / "list_test.py"
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("A")
def a(ctx): pass

@stage("B")
def b(ctx): pass

@stage("C")
def c(ctx): pass
"""
    )
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    runner = WorkflowRunner(ctx)
    names = runner.list_stages(wf)
    assert names == ["A", "B", "C"]


def test_runner_persists_variables(tmp_path):
    wf = tmp_path / "persist.py"
    wf.write_text(
        """\
from restful.workflow.decorator import stage

@stage("Set")
def set_it(ctx):
    ctx.set("persisted", "yes")
"""
    )
    vs = VariableStore(tmp_path)
    ctx = WorkflowContext(variables=vs)
    runner = WorkflowRunner(ctx)
    runner.run(wf)

    # Reload from disk
    vs2 = VariableStore(tmp_path)
    assert vs2.get("persisted") == "yes"
