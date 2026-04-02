# Client API

The `Client` class is the core REST client. It takes typed `Endpoint` objects and handles authentication, OData parameters, and error recovery.

## Constructor

```python
from restful import Client, BearerAuth

client = Client(
    base_url="https://api.example.com",
    auth=BearerAuth(...),       # optional
    verify_tls=False,           # default: False
    timeout_s=15,               # default: 15
)
```

## Methods

All methods share the same signature pattern:

```python
client.get(endpoint, *, params=None, query=None, expected_status=200)
client.post(endpoint, *, params=None, query=None, payload=None, expected_status={200, 201})
client.put(endpoint, *, params=None, query=None, payload=None, expected_status={200, 201})
client.delete(endpoint, *, params=None, query=None, payload=None, expected_status={200, 201, 204})
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `endpoint` | `Endpoint` | Typed endpoint constant |
| `params` | `dict[str, str]` | OData key predicates — `{"id": "123"}` → `/Nodes(123)` |
| `query` | `dict[str, Any]` | URL query parameters — `{"limit": 10}` → `?limit=10` |
| `payload` | `Any` | JSON request body (POST/PUT/DELETE) |
| `expected_status` | `int \| set[int]` | Expected HTTP status code(s) |

### OData Key Predicates

For endpoints with path parameters like `/Nodes({id},{namespace})`:

```python
response = client.get(Nodes, params={"id": "abc", "namespace": "prod"})
# → GET /redfish/v1/SFM/1/Infrastructures/Nodes(abc,prod)
```

Values are URL-encoded via `urllib.parse.quote`.

## Response

All methods return `HttpResponse`:

```python
response = client.get(BlueprintTemplates)
response.status_code    # 200
response.json()         # parsed JSON body
response.text           # raw response text
response.headers        # dict of response headers
response.method         # "GET"
response.url            # full URL that was called
response.show()         # pretty-print to stdout
```

## 401 Retry

When a request returns 401 and the client has auth configured:

1. `auth.invalidate()` — clear cached credentials
2. `auth.auth_headers()` — re-authenticate (triggers fresh login)
3. Retry the original request once

If the retry also fails, the error is raised.

## Context Manager

```python
with Client(base_url="https://api.example.com") as client:
    response = client.get(endpoint)
# session closed automatically
```
