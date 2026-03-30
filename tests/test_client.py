from unittest.mock import MagicMock

import pytest

from post_it.client import Client
from post_it.http.errors import HttpError
from post_it.http.models import HttpResponse
from post_it.models import Endpoint


def _mock_auth():
    auth = MagicMock()
    auth.auth_headers.return_value = {"Authorization": "Bearer fake"}
    return auth


def test_resolve_path_no_params():
    client = Client(base_url="https://test", auth=_mock_auth())
    ep = Endpoint(path="/api/v1/nodes", methods=("GET",))
    assert client._resolve_path(ep, None) == "/api/v1/nodes"


def test_resolve_path_with_params():
    client = Client(base_url="https://test", auth=_mock_auth())
    ep = Endpoint(path="/api/v1/nodes", methods=("GET",))
    path = client._resolve_path(ep, {"id": "abc", "ns": "prod"})
    assert path == "/api/v1/nodes(abc,prod)"


def test_401_retry():
    auth = _mock_auth()
    client = Client(base_url="https://test", auth=auth)
    ep = Endpoint(path="/api/v1/nodes", methods=("GET",))

    ok = HttpResponse(status_code=200, method="GET", url="https://test/api/v1/nodes", headers={}, text="{}")
    call_count = 0

    def fake_request(method, path, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise HttpError(method="GET", url=path, status_code=401, body="Unauthorized")
        return ok

    client.http.request = fake_request  # ty: ignore[invalid-assignment]
    resp = client.get(ep)
    assert resp.status_code == 200
    assert call_count == 2
    auth.invalidate.assert_called_once()


def test_non_401_raises():
    client = Client(base_url="https://test", auth=_mock_auth())
    ep = Endpoint(path="/api/v1/nodes", methods=("GET",))

    def fake_request(method, path, **kwargs):
        raise HttpError(method="GET", url=path, status_code=500, body="Error")

    client.http.request = fake_request  # ty: ignore[invalid-assignment]
    with pytest.raises(HttpError) as exc:
        client.get(ep)
    assert exc.value.status_code == 500


def test_response_str_format():
    resp = HttpResponse(
        status_code=200,
        method="GET",
        url="https://test/api/v1/nodes",
        headers={},
        text='{"nodes": []}',
    )
    output = str(resp)
    assert "GET 200 /api/v1/nodes" in output
    assert '"nodes"' in output


def test_context_manager():
    client = Client(base_url="https://test", auth=_mock_auth())
    with client as c:
        assert c is client
    client.close()
