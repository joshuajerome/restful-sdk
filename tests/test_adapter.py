from pathlib import Path

from post_it.plugins.snf_instance_rest.adapter import SnfInstanceRestAdapter

RBAC_PATH = (
    Path(__file__).resolve().parents[1] / ".." / "cutip-projects" / "pre-cutip" / "sfmpost" / "rbac_access_matrix.json"
)


def test_parse_count():
    adapter = SnfInstanceRestAdapter()
    specs = adapter.parse(RBAC_PATH)
    assert len(specs) == 219


def test_parse_transforms_snf_to_sfm():
    adapter = SnfInstanceRestAdapter()
    specs = adapter.parse(RBAC_PATH)
    sfm_paths = [s for s in specs if s.path.startswith("/redfish/v1/SFM/1/")]
    # Most endpoints should be transformed (except v2 ones)
    assert len(sfm_paths) >= 217


def test_parse_extracts_methods():
    adapter = SnfInstanceRestAdapter()
    specs = adapter.parse(RBAC_PATH)
    nodes = next(s for s in specs if s.name == "Nodes")
    assert "GET" in nodes.methods
    assert "POST" in nodes.methods


def test_parse_names_are_unique():
    adapter = SnfInstanceRestAdapter()
    specs = adapter.parse(RBAC_PATH)
    names = [s.name for s in specs]
    assert len(names) == len(set(names))


def test_parse_carries_access_group_metadata():
    adapter = SnfInstanceRestAdapter()
    specs = adapter.parse(RBAC_PATH)
    nodes = next(s for s in specs if s.name == "Nodes")
    assert "access_groups" in nodes.metadata
    assert "access-groups-for-get" in nodes.metadata["access_groups"]
