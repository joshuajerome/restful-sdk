# Endpoint Model

## Endpoint (runtime)

The frozen dataclass used in user code:

```python
from restful.models import Endpoint

BlueprintTemplates = Endpoint(
    path="/redfish/v1/SFM/1/BlueprintTemplates",
    methods=("GET",),
)
```

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | URL path (may contain OData placeholders) |
| `methods` | `tuple[str, ...]` | Supported HTTP methods |

## EndpointSpec (ingestion)

The intermediate format produced by plugin adapters:

```python
from restful.models import EndpointSpec

spec = EndpointSpec(
    path="/redfish/v1/SFM/1/BlueprintTemplates",
    methods=("GET",),
    name="BlueprintTemplates",
    description="List all blueprint templates",
    metadata={"roles": ["admin", "operator"]},
)
```

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | URL path |
| `methods` | `tuple[str, ...]` | HTTP methods |
| `name` | `str` | PascalCase constant name |
| `description` | `str` | Human-readable description |
| `metadata` | `dict` | Plugin-specific extra data |
