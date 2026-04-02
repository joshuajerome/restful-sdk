# Plugin Adapter

Plugins implement the `Adapter` protocol to parse API specification files into `EndpointSpec` objects.

## Protocol

```python
class Adapter:
    name: str

    def parse(self, source: Path) -> list[EndpointSpec]:
        ...
```

| Field/Method | Description |
|-------------|-------------|
| `name` | Unique plugin identifier (used in config `plugin:` field) |
| `parse()` | Read source file, return normalized endpoint specs |

## Registry

```python
from restful.plugins.registry import registry

# List all plugins
registry.list_plugins()  # ["snf-instance-rest"]

# Get a plugin
adapter = registry.get("snf-instance-rest")

# Register a custom plugin
registry.register(MyAdapter())
```

## Custom Plugins

To create a custom plugin, place it in a directory and reference it via `plugin_path` in your workspace config:

```yaml
apis:
  - name: My API
    alias: myapi
    plugin: my-custom-plugin
    plugin_path: ./plugins
    source: my_spec.json
```

The plugin module must expose an `Adapter` class or instance with `name` and `parse()`.
