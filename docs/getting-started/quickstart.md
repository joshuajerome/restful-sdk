# Quickstart

This guide walks you through creating a workspace, loading an API plugin, and making your first REST call.

## 1. Create a Workspace

```bash
python -m restful workspace create -n my-project
cd my-project
```

This creates:

```
my-project/
├── my-project.config.yaml
├── __main__.py
├── apis/
├── workflows/
└── .restful/
```

## 2. Configure an API

Edit `my-project.config.yaml`:

```yaml
name: my-project
apis:
  - name: My API
    alias: myapi
    plugin: snf-instance-rest
    source: rbac_access_matrix.json
    base_url: https://api.example.com
    auth:
      type: bearer
      login_path: /security/v1/auth/login
      username: admin
      password_env: MY_API_PASSWORD
```

Key fields:

- **alias** — the Python-friendly name used in workflows: `ctx.clients.myapi`
- **plugin** — which adapter parses the source file
- **source** — relative path to the API spec/schema file
- **password_env** — environment variable holding the password (never hardcode secrets)

## 3. Load the Plugin

```bash
python -m restful plugin validate
python -m restful plugin load
```

This generates `apis/my_api/endpoints.py` with typed `Endpoint` constants.

## 4. Make a Request

```python
from restful import Client, BearerAuth

client = Client(
    base_url="https://api.example.com",
    auth=BearerAuth(
        base_url="https://api.example.com",
        login_path="/security/v1/auth/login",
        payload={"username": "admin", "password": "secret"},
    ),
)

from apis.my_api.endpoints import BlueprintTemplates
response = client.get(BlueprintTemplates)
print(response.json())
```

## 5. Write a Workflow

Create `workflows/my_flow.py`:

```python
from restful import stage, WorkflowContext

@stage("Fetch data")
def fetch_data(ctx: WorkflowContext):
    from apis.my_api.endpoints import BlueprintTemplates
    response = ctx.clients.myapi.get(BlueprintTemplates)
    ctx.set("count", str(len(response.json().get("items", []))))

@stage("Report")
def report(ctx: WorkflowContext):
    count = ctx.get("count")
    print(f"Found {count} items")
```

Run it:

```bash
python -m restful workflow run my_flow
```

## Next Steps

- [Workspace Layout](workspace-layout.md) — understand the full directory structure
- [Concepts: Workflows](../concepts/workflows.md) — learn about stages, context, and runners
- [Reference: CLI](../reference/cli.md) — all available commands
