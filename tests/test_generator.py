from post_it.generator.python_module import generate
from post_it.models import EndpointSpec


def test_generate_produces_valid_source():
    specs = [
        EndpointSpec(path="/api/v1/users", methods=("GET", "POST"), name="Users"),
        EndpointSpec(path="/api/v1/items", methods=("GET",), name="Items"),
    ]
    source = generate(specs, plugin_name="test")
    assert 'Users = Endpoint(path="/api/v1/users"' in source
    assert 'Items = Endpoint(path="/api/v1/items"' in source
    assert "from post_it.models import Endpoint" in source


def test_generate_includes_all_methods():
    specs = [
        EndpointSpec(path="/api/v1/data", methods=("GET", "POST", "DELETE"), name="Data"),
    ]
    source = generate(specs)
    assert '"GET"' in source
    assert '"POST"' in source
    assert '"DELETE"' in source


def test_generate_empty_specs():
    source = generate([])
    assert "Endpoints: 0" in source
    assert "Endpoint(" not in source
