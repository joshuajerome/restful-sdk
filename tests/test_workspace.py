"""Tests for workspace config, discovery, scaffold, and variables."""

import pytest

from restful.workspace.config import WorkspaceConfig, _sanitize_name
from restful.workspace.scaffold import create_workspace
from restful.workspace.variables import VariableStore

# ─── Config ──────────────────────────────────────────────────────────────


def test_sanitize_name():
    assert _sanitize_name("snf-instance-rest") == "snf_instance_rest"
    assert _sanitize_name("My API Name") == "my_api_name"
    assert _sanitize_name("  UPPER--CASE  ") == "upper_case"
    assert _sanitize_name("") == "unnamed"


def test_load_config(tmp_path):
    config = tmp_path / "test.config.yaml"
    config.write_text(
        """\
apiVersion: post-it/v1
workspace:
  name: test-ws
apis:
  - name: my-api
    alias: api
    plugin: snf-instance-rest
    source: data.json
    auth:
      type: bearer
      login_path: /login
      username: admin
      password_env: MY_PW
"""
    )
    ws = WorkspaceConfig.load(config)
    assert ws.name == "test-ws"
    assert len(ws.apis) == 1
    assert ws.apis[0].alias == "api"
    assert ws.apis[0].auth.type == "bearer"
    assert ws.apis[0].auth.password_env == "MY_PW"


def test_config_missing_api_name(tmp_path):
    config = tmp_path / "bad.config.yaml"
    config.write_text("apiVersion: post-it/v1\nworkspace:\n  name: x\napis:\n  - plugin: p\n    source: s\n")
    with pytest.raises(ValueError, match="missing 'name'"):
        WorkspaceConfig.load(config)


def test_config_duplicate_aliases(tmp_path):
    config = tmp_path / "dup.config.yaml"
    config.write_text(
        """\
apiVersion: post-it/v1
workspace:
  name: x
apis:
  - name: a
    alias: same
    plugin: p
    source: s
  - name: b
    alias: same
    plugin: p
    source: s
"""
    )
    with pytest.raises(ValueError, match="Duplicate"):
        WorkspaceConfig.load(config)


def test_config_auto_alias(tmp_path):
    config = tmp_path / "auto.config.yaml"
    config.write_text(
        """\
apiVersion: post-it/v1
workspace:
  name: x
apis:
  - name: snf-instance-rest
    plugin: snf-instance-rest
    source: data.json
"""
    )
    ws = WorkspaceConfig.load(config)
    assert ws.apis[0].alias == "snf_instance_rest"


def test_config_not_yaml_mapping(tmp_path):
    config = tmp_path / "list.config.yaml"
    config.write_text("[1, 2, 3]")
    with pytest.raises(ValueError, match="YAML mapping"):
        WorkspaceConfig.load(config)


# ─── Scaffold ────────────────────────────────────────────────────────────


def test_scaffold_creates_structure(tmp_path):
    root = create_workspace("myws", parent=tmp_path)
    assert root.exists()
    assert (root / "myws.config.yaml").exists()
    assert (root / "__main__.py").exists()
    assert (root / "apis" / "__init__.py").exists()
    assert (root / "notebooks").is_dir()
    assert (root / ".restful").is_dir()
    assert (root / ".gitignore").exists()


def test_scaffold_rejects_existing(tmp_path):
    (tmp_path / "existing").mkdir()
    with pytest.raises(FileExistsError):
        create_workspace("existing", parent=tmp_path)


# ─── Variables ───────────────────────────────────────────────────────────


def test_variable_store_set_get(tmp_path):
    vs = VariableStore(tmp_path)
    vs.set("key1", "value1")
    assert vs.get("key1") == "value1"
    assert vs.get("nonexistent") is None


def test_variable_store_persist(tmp_path):
    vs = VariableStore(tmp_path)
    vs.set("persist_key", "persist_val")
    vs.save()

    vs2 = VariableStore(tmp_path)
    assert vs2.get("persist_key") == "persist_val"


def test_variable_store_delete(tmp_path):
    vs = VariableStore(tmp_path)
    vs.set("k", "v")
    vs.delete("k")
    assert vs.get("k") is None


def test_variable_store_all(tmp_path):
    vs = VariableStore(tmp_path)
    vs.set("a", "1")
    vs.set("b", "2")
    assert vs.all() == {"a": "1", "b": "2"}


def test_variable_store_coerces_to_string(tmp_path):
    vs = VariableStore(tmp_path)
    vs.set("num", 42)
    assert vs.get("num") == "42"
