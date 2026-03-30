import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


def _run(args: list[str], cwd: Path = PROJECT_DIR) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "post_it"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_plugins_command():
    r = _run(["plugins"])
    assert r.returncode == 0
    assert "snf-instance-rest" in r.stdout


def test_validate_command():
    r = _run(["validate"])
    assert r.returncode == 0
    assert "Valid" in r.stdout
    assert "219" in r.stdout


def test_generate_command(tmp_path):
    # Create a temp post-it.yaml pointing to rbac JSON
    rbac = PROJECT_DIR / ".." / "cutip-projects" / "pre-cutip" / "sfmpost" / "rbac_access_matrix.json"
    config = tmp_path / "post-it.yaml"
    output = tmp_path / "endpoints.py"
    config.write_text(f"project: test\nplugin: snf-instance-rest\nsource: {rbac.resolve()}\nendpoints: {output}\n")

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
