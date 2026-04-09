"""
Workspace setup — create a workspace, configure an API, load endpoints.

This script demonstrates the programmatic workspace API.
Most users will do this via the CLI or the desktop app instead.
"""

from pathlib import Path

from restful.workspace.scaffold import create_workspace
from restful.workspace.config import WorkspaceConfig
from restful.workspace.variables import VariableStore

# ── Create a workspace ───────────────────────────────────────────────────

workspace_dir = Path("/tmp/restful-example")
if not workspace_dir.exists():
    root = create_workspace("restful-example", parent=Path("/tmp"))
    print(f"Created workspace: {root}")
else:
    root = workspace_dir
    print(f"Workspace exists: {root}")

# ── Examine the structure ────────────────────────────────────────────────

print(f"\nWorkspace structure:")
for p in sorted(root.rglob("*")):
    if "__pycache__" in str(p):
        continue
    rel = p.relative_to(root)
    indent = "  " * len(rel.parts)
    print(f"  {indent}{rel.name}{'/' if p.is_dir() else ''}")

# ── Load the config ──────────────────────────────────────────────────────

config_path = root / "restful-example.config.yaml"
config = WorkspaceConfig.load(config_path)
print(f"\nWorkspace name: {config.name}")
print(f"APIs configured: {len(config.apis)}")

# ── Use variables ────────────────────────────────────────────────────────

vs = VariableStore(root)
vs.set("environment", "development")
vs.set("api_version", "v1")
vs.save()

print(f"\nVariables:")
for k, v in vs.all().items():
    print(f"  {k} = {v}")

# ── Cleanup note ─────────────────────────────────────────────────────────

print(f"\nTo clean up: rm -rf {root}")
