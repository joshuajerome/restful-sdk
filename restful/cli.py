"""restful CLI — workspace, plugin, and workflow management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from restful.generator.python_module import generate
from restful.plugins import registry
from restful.workflow.context import WorkflowContext
from restful.workflow.runner import WorkflowRunner
from restful.workspace.config import WorkspaceConfig
from restful.workspace.discovery import load_workspace
from restful.workspace.scaffold import create_workspace
from restful.workspace.variables import VariableStore

# ─── Helpers ────────────────────────────────────────────────────────────


def _load_ws() -> WorkspaceConfig:
    """Load workspace from cwd, exit on failure."""
    try:
        return load_workspace()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading workspace: {e}")
        sys.exit(1)


def _resolve_plugin(plugin_name: str, plugin_path: str = ""):
    """Resolve a plugin adapter by name (if already loaded) or path."""
    # Check if already registered
    adapter = registry.get(plugin_name)
    if adapter:
        return adapter

    # Try to load from plugin_path
    if plugin_path:
        p = Path(plugin_path)
        try:
            adapter = registry.load_plugin(p)
            return adapter
        except Exception as e:
            print(f"Error loading plugin from {plugin_path}: {e}")
            sys.exit(1)

    print(f"Error: Plugin '{plugin_name}' not registered and no plugin_path specified")
    registered = registry.list_plugins()
    if registered:
        print(f"Registered plugins: {', '.join(registered)}")
    sys.exit(1)


# ─── Workspace Commands ─────────────────────────────────────────────────


def cmd_workspace_create(args: argparse.Namespace) -> None:
    name = args.name
    try:
        root = create_workspace(name)
        print(f"Created workspace: {root}")
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_workspace_info(args: argparse.Namespace) -> None:
    ws = _load_ws()
    print(f"Workspace: {ws.name}")
    print(f"Config: {ws.config_path}")
    print(f"Root: {ws.root}")
    print(f"APIs: {len(ws.apis)}")
    for api in ws.apis:
        print(f"  - {api.name} (alias: {api.alias}, plugin: {api.plugin})")


def cmd_workspace_vars(args: argparse.Namespace) -> None:
    ws = _load_ws()
    vs = VariableStore(ws.root)

    if args.vars_action == "set":
        vs.set(args.key, args.value)
        vs.save()
        print(f"Set {args.key} = {args.value}")
    elif args.vars_action == "delete":
        vs.delete(args.key)
        vs.save()
        print(f"Deleted {args.key}")
    else:
        # List
        variables = vs.all()
        if not variables:
            print("No variables set.")
            return
        for k, v in sorted(variables.items()):
            display = v if len(v) <= 60 else v[:57] + "..."
            print(f"  {k} = {display}")


# ─── Plugin Commands ─────────────────────────────────────────────────────


def cmd_plugin_list(args: argparse.Namespace) -> None:
    plugins = registry.list_plugins()
    if not plugins:
        print("No plugins registered. Use plugin_path in workspace config to load plugins.")
        return
    print("Registered plugins:")
    for name in plugins:
        print(f"  {name}")


def cmd_plugin_validate(args: argparse.Namespace) -> None:
    ws = _load_ws()
    apis = ws.apis if not args.name else [a for a in ws.apis if a.name == args.name]

    if args.name and not apis:
        print(f"Error: API '{args.name}' not found in config")
        sys.exit(1)

    for api in apis:
        adapter = _resolve_plugin(api.plugin, api.plugin_path)
        source = ws.root / api.source
        if not source.exists():
            print(f"✗ {api.name}: source not found: {source}")
            continue
        try:
            specs = adapter.parse(source)
            print(f"✓ {api.name}: plugin OK, source OK, {len(specs)} endpoints")
        except Exception as e:
            print(f"✗ {api.name}: parse error: {e}")


def cmd_plugin_load(args: argparse.Namespace) -> None:
    ws = _load_ws()
    apis = ws.apis if not args.name else [a for a in ws.apis if a.name == args.name]

    if args.name and not apis:
        print(f"Error: API '{args.name}' not found in config")
        sys.exit(1)

    for api in apis:
        adapter = _resolve_plugin(api.plugin, api.plugin_path)
        source = ws.root / api.source
        if not source.exists():
            print(f"✗ {api.name}: source not found: {source}")
            continue

        try:
            specs = adapter.parse(source)
        except Exception as e:
            print(f"✗ {api.name}: parse error: {e}")
            continue

        # Generate into apis/<sanitized_name>/endpoints.py
        from restful.workspace.config import _sanitize_name

        api_dir = ws.root / "apis" / _sanitize_name(api.name)
        api_dir.mkdir(parents=True, exist_ok=True)

        endpoints_path = api_dir / "endpoints.py"
        source_code = generate(specs, plugin_name=api.plugin)
        endpoints_path.write_text(source_code, encoding="utf-8")

        init_path = api_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text("", encoding="utf-8")

        print(f"Loaded {api.name}: {len(specs)} endpoints → {endpoints_path.relative_to(ws.root)}")


# ─── Workflow Commands ───────────────────────────────────────────────────


def cmd_workflow_list(args: argparse.Namespace) -> None:
    ws = _load_ws()
    wf_dir = ws.root / "workflows"
    if not wf_dir.exists():
        print("No workflows/ directory found.")
        return
    workflows = sorted(wf_dir.glob("*.py"))
    if not workflows:
        print("No workflow files found.")
        return
    for wf in workflows:
        if wf.name.startswith("_"):
            continue
        print(f"  {wf.stem}")


def cmd_workflow_run(args: argparse.Namespace) -> None:
    ws = _load_ws()

    # Find workflow file
    wf_path = ws.root / "workflows" / f"{args.workflow_name}.py"
    if not wf_path.exists():
        # Try exact path
        wf_path = Path(args.workflow_name)
        if not wf_path.exists():
            print(f"Error: Workflow not found: {args.workflow_name}")
            sys.exit(1)

    # Add workspace root to sys.path for imports
    import sys as _sys

    ws_root = str(ws.root)
    if ws_root not in _sys.path:
        _sys.path.insert(0, ws_root)

    ctx = WorkflowContext.from_workspace(ws)
    runner = WorkflowRunner(ctx)

    if args.list_stages:
        stages = runner.list_stages(wf_path)
        if not stages:
            print("No @stage functions found.")
            return
        for i, name in enumerate(stages, 1):
            print(f"  {i}. {name}")
        return

    if args.stage:
        result = runner.run_stage(wf_path, args.stage)
        _print_result(result)
    else:
        results = runner.run(wf_path)
        for r in results:
            _print_result(r)
        print(f"\n{'─' * 40}")
        passed = sum(1 for r in results if r.success)
        print(f"Completed: {passed}/{len(results)} stages")


def _print_result(result) -> None:
    status = "✓" if result.success else "✗"
    print(f"  {status} {result.stage_name} ({result.duration_ms}ms)")
    if result.error:
        print(f"    Error: {result.error}")
    if result.captured_vars:
        for k, v in result.captured_vars.items():
            display = v if len(v) <= 50 else v[:47] + "..."
            print(f"    → {k} = {display}")


# ─── Backwards-compatible commands (from old CLI) ────────────────────────


def cmd_generate(args: argparse.Namespace) -> None:
    """Legacy: generate from restful.yaml (old format)."""
    from restful.config import PostItConfig

    try:
        config = PostItConfig.load(Path(args.config))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    adapter = _resolve_plugin(config.plugin, config.plugin_path)

    source = Path(config.source)
    if not source.exists():
        print(f"Error: Source file not found: {source}")
        sys.exit(1)

    try:
        specs = adapter.parse(source)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    source_code = generate(specs, plugin_name=config.plugin)
    output = Path(config.endpoints)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source_code, encoding="utf-8")
    print(f"Generated {output} ({len(specs)} endpoints)")


def cmd_validate(args: argparse.Namespace) -> None:
    """Legacy: validate from restful.yaml (old format)."""
    from restful.config import PostItConfig

    try:
        config = PostItConfig.load(Path(args.config))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    adapter = _resolve_plugin(config.plugin, config.plugin_path)

    source = Path(config.source)
    if not source.exists():
        print(f"Error: Source file not found: {source}")
        sys.exit(1)

    try:
        specs = adapter.parse(source)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Valid. Plugin: {config.plugin}, Source: {config.source}, Endpoints: {len(specs)}")


# ─── Main ────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="restful",
        description="REST workflow tool — workspaces, plugins, and workflows",
    )
    sub = parser.add_subparsers(dest="command")

    # --- workspace ---
    ws_parser = sub.add_parser("workspace", help="Workspace management")
    ws_sub = ws_parser.add_subparsers(dest="ws_action")

    ws_create = ws_sub.add_parser("create", help="Create a new workspace")
    ws_create.add_argument("-n", "--name", required=True, help="Workspace name")

    ws_sub.add_parser("info", help="Show workspace info")

    ws_vars = ws_sub.add_parser("vars", help="Manage workspace variables")
    ws_vars_sub = ws_vars.add_subparsers(dest="vars_action")
    ws_vars_set = ws_vars_sub.add_parser("set", help="Set a variable")
    ws_vars_set.add_argument("key", help="Variable name")
    ws_vars_set.add_argument("value", help="Variable value")
    ws_vars_del = ws_vars_sub.add_parser("delete", help="Delete a variable")
    ws_vars_del.add_argument("key", help="Variable name")

    # --- plugin ---
    pl_parser = sub.add_parser("plugin", help="Plugin management")
    pl_sub = pl_parser.add_subparsers(dest="pl_action")

    pl_sub.add_parser("list", help="List registered plugins")

    pl_validate = pl_sub.add_parser("validate", help="Validate plugins and sources")
    pl_validate.add_argument("-n", "--name", help="Validate specific API by name")

    pl_load = pl_sub.add_parser("load", help="Load plugins and generate endpoints")
    pl_load.add_argument("-n", "--name", help="Load specific API by name")

    # --- workflow ---
    wf_parser = sub.add_parser("workflow", help="Workflow management")
    wf_sub = wf_parser.add_subparsers(dest="wf_action")

    wf_sub.add_parser("list", help="List workflows in workspace")

    wf_run = wf_sub.add_parser("run", help="Run a workflow")
    wf_run.add_argument("workflow_name", help="Workflow file name (without .py)")
    wf_run.add_argument("--stage", help="Run a single stage by name")
    wf_run.add_argument("--list", dest="list_stages", action="store_true", help="List stages")

    # --- legacy (backwards compatible) ---
    config_arg = argparse.ArgumentParser(add_help=False)
    config_arg.add_argument("-c", "--config", default="restful.yaml", help="Config file")

    sub.add_parser("generate", parents=[config_arg], help="Generate endpoints (legacy)")
    sub.add_parser("validate", parents=[config_arg], help="Validate config (legacy)")
    sub.add_parser("plugins", help="List plugins (legacy)")

    args = parser.parse_args()

    # Dispatch
    if args.command == "workspace":
        actions = {"create": cmd_workspace_create, "info": cmd_workspace_info, "vars": cmd_workspace_vars}
        handler = actions.get(args.ws_action)
        if handler:
            handler(args)
        else:
            ws_parser.print_help()

    elif args.command == "plugin":
        actions = {"list": cmd_plugin_list, "validate": cmd_plugin_validate, "load": cmd_plugin_load}
        handler = actions.get(args.pl_action)
        if handler:
            handler(args)
        else:
            pl_parser.print_help()

    elif args.command == "workflow":
        actions = {"list": cmd_workflow_list, "run": cmd_workflow_run}
        handler = actions.get(args.wf_action)
        if handler:
            handler(args)
        else:
            wf_parser.print_help()

    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "plugins":
        cmd_plugin_list(args)
    else:
        parser.print_help()
        sys.exit(1)
