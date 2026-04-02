import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DIR = PROJECT_DIR / ".." / "sfm-util" / "plugins" / "snf-instance-rest"
RBAC_PATH = PROJECT_DIR / ".." / "cutip-projects" / "pre-cutip" / "sfmpost" / "rbac_access_matrix.json"

needs_external = pytest.mark.skipif(
    not PLUGIN_DIR.exists() or not RBAC_PATH.exists(),
    reason="Requires external sfm-util plugin and rbac_access_matrix.json",
)


def _run(args: list[str], cwd: Path = PROJECT_DIR) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "restful"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_plugins_command():
    r = _run(["plugins"])
    assert r.returncode == 0
    assert "no plugins" in r.stdout.lower() or r.stdout.strip() == ""


@needs_external
def test_validate_command():
    r = _run(["validate"])
    assert r.returncode == 0
    assert "Valid" in r.stdout
    assert "219" in r.stdout


@needs_external
def test_generate_command(tmp_path):
    config = tmp_path / "restful.yaml"
    output = tmp_path / "endpoints.py"
    config.write_text(
        f"project: test\n"
        f"plugin: snf-instance-rest\n"
        f"plugin_path: {PLUGIN_DIR.resolve()}\n"
        f"source: {RBAC_PATH.resolve()}\n"
        f"endpoints: {output}\n"
    )

    r = _run(["generate", "-c", str(config)])
    assert r.returncode == 0
    assert "219 endpoints" in r.stdout
    assert output.exists()
    content = output.read_text()
    assert "BlueprintTemplates" in content


def test_validate_missing_config(tmp_path):
    r = _run(["validate", "-c", str(tmp_path / "nonexistent.yaml")])
    assert r.returncode != 0
    assert "not found" in r.stdout.lower() or "error" in r.stdout.lower()
