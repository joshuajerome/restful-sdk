from pathlib import Path

import pytest

from restful.plugins import registry

PLUGIN_DIR = (
    Path(__file__).resolve().parents[1] / ".." / "sfm-util" / "plugins" / "snf-instance-rest"
)

RBAC_PATH = (
    Path(__file__).resolve().parents[1] / ".." / "cutip-projects" / "pre-cutip" / "sfmpost" / "rbac_access_matrix.json"
)


def _get_adapter():
    adapter = registry.get("snf-instance-rest")
    if adapter is None:
        adapter = registry.load_plugin(PLUGIN_DIR)
    return adapter


needs_plugin = pytest.mark.skipif(
    not PLUGIN_DIR.exists() or not RBAC_PATH.exists(),
    reason="Requires external sfm-util plugin and rbac_access_matrix.json",
)


@needs_plugin
def test_parse_count():
    adapter = _get_adapter()
    specs = adapter.parse(RBAC_PATH)
    assert len(specs) == 219


@needs_plugin
def test_parse_transforms_snf_to_sfm():
    adapter = _get_adapter()
    specs = adapter.parse(RBAC_PATH)
    sfm_paths = [s for s in specs if s.path.startswith("/redfish/v1/SFM/1/")]
    # Most endpoints should be transformed (except v2 ones)
    assert len(sfm_paths) >= 217


@needs_plugin
def test_parse_extracts_methods():
    adapter = _get_adapter()
    specs = adapter.parse(RBAC_PATH)
    nodes = next(s for s in specs if s.name == "Nodes")
    assert "GET" in nodes.methods
    assert "POST" in nodes.methods


@needs_plugin
def test_parse_names_are_unique():
    adapter = _get_adapter()
    specs = adapter.parse(RBAC_PATH)
    names = [s.name for s in specs]
    assert len(names) == len(set(names))


@needs_plugin
def test_parse_carries_access_group_metadata():
    adapter = _get_adapter()
    specs = adapter.parse(RBAC_PATH)
    nodes = next(s for s in specs if s.name == "Nodes")
    assert "access_groups" in nodes.metadata
    assert "access-groups-for-get" in nodes.metadata["access_groups"]
