# Writing a Plugin

This guide walks through creating a custom plugin adapter for a new API specification format.

## 1. Create the Adapter

```python
# plugins/my_adapter.py
from pathlib import Path
from restful.models import EndpointSpec

class MyAdapter:
    name = "my-custom-plugin"

    def parse(self, source: Path) -> list[EndpointSpec]:
        import json
        data = json.loads(source.read_text())

        specs = []
        for entry in data["endpoints"]:
            specs.append(EndpointSpec(
                path=entry["path"],
                methods=tuple(entry["methods"]),
                name=entry["name"],
                description=entry.get("description", ""),
            ))
        return specs
```

## 2. Reference in Config

```yaml
apis:
  - name: My API
    alias: myapi
    plugin: my-custom-plugin
    plugin_path: ./plugins
    source: my_spec.json
    base_url: https://api.example.com
```

The `plugin_path` tells restful where to find the adapter module.

## 3. Validate and Load

```bash
python -m restful plugin validate -n myapi
python -m restful plugin load -n myapi
```

## Tips

- Return consistent PascalCase names for endpoint constants
- Handle duplicate names by appending `_N` suffixes
- Include `description` for better documentation
- Use `metadata` for plugin-specific data (roles, permissions, etc.)
