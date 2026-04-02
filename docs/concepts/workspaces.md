# Workspaces

A workspace is the unit of organization in restful. It groups API connections, generated endpoints, workflows, and runtime state into a single directory.

## Discovery

restful discovers workspaces by walking up from the current directory until it finds a `*.config.yaml` file. This means you can run `restful` commands from any subdirectory.

```python
from restful.workspace.discovery import load_workspace

config = load_workspace()  # discovers from cwd
config = load_workspace(Path("/path/to/workspace"))  # explicit path
```

## Config File

```yaml
name: my-workspace
apis:
  - name: SFM Instance REST
    alias: sfm
    plugin: snf-instance-rest
    source: rbac_access_matrix.json
    base_url: https://100.94.115.90
    auth:
      type: bearer
      login_path: /security/v1/auth/login
      username: admin
      password_env: SFM_PASSWORD

  - name: Netbox
    alias: netbox
    plugin: custom-adapter
    plugin_path: ./plugins
    source: netbox_spec.json
    base_url: https://netbox.example.com
    auth:
      type: apikey
      header: Authorization
      key_env: NETBOX_API_KEY
```

## API Connection Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the API |
| `alias` | Yes | Python identifier used as `ctx.clients.<alias>` |
| `plugin` | Yes | Adapter name (built-in or custom) |
| `source` | Yes | Relative path to the API spec file |
| `base_url` | No | Base URL for HTTP requests |
| `plugin_path` | No | Directory containing custom plugin module |
| `auth.type` | No | `bearer`, `apikey`, or `none` (default: `none`) |

## Scaffolding

```bash
python -m restful workspace create -n my-project
```

Creates a complete workspace directory with config template, `__main__.py`, `apis/`, `workflows/`, `.restful/`, and `.gitignore`.
