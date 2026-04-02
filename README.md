# restful-sdk

REST workflow automation framework — ingest API endpoint definitions, generate typed Python modules, and orchestrate multi-step REST workflows.

## Install

```bash
pip install restful-sdk
```

## Quick Example

```python
from restful import Client, BearerAuth, stage, WorkflowContext

# Direct client usage
client = Client(
    base_url="https://api.example.com",
    auth=BearerAuth(
        base_url="https://api.example.com",
        login_path="/auth/login",
        payload={"username": "admin", "password": "secret"},
    ),
)

# Import generated endpoints (typed constants with IDE autocomplete)
from apis.my_api.endpoints import Devices, Interfaces

response = client.get(Devices)
print(response.json())

# OData key predicates
response = client.get(Interfaces, params={"id": "eth0", "device": "switch1"})
# → GET /interfaces(eth0,switch1)
```

## Workspaces

A workspace groups API connections, generated endpoints, and workflows into a single directory.

```bash
# Create a workspace
python -m restful workspace create -n my-project
cd my-project

# Configure APIs in my-project.config.yaml, then:
python -m restful plugin load        # generate typed endpoint modules
python -m restful workflow run flow  # run a workflow
```

**Workspace layout:**

```
my-project/
├── my-project.config.yaml    # API connections, auth, plugins
├── apis/
│   └── my_api/
│       └── endpoints.py      # auto-generated Endpoint constants
├── workflows/
│   └── flow.py               # @stage-decorated Python scripts
└── .restful/
    ├── cache.json             # token cache (per base URL)
    └── variables.json         # workspace variables
```

## Workflows

Chain REST calls into sequential stages with shared context:

```python
from restful import stage, WorkflowContext

@stage("Fetch devices")
def fetch(ctx: WorkflowContext):
    response = ctx.clients.myapi.get(Devices)
    ctx.set("count", str(len(response.json()["items"])))

@stage("Report")
def report(ctx: WorkflowContext):
    print(f"Found {ctx.get('count')} devices")
```

```bash
python -m restful workflow run flow
#   [ok] Fetch devices (245ms)
#       count = 12
#   [ok] Report (3ms)
```

## Plugins

Plugins parse API specification files into typed endpoint modules. A plugin is a directory with `plugin.yaml` + `adapter.py`:

```
my-plugin/
├── plugin.yaml      # name, version, description
└── adapter.py       # name (str) + parse(Path) -> list[EndpointSpec]
```

No built-in plugins — reference them via `plugin_path` in your workspace config.

## Key Features

- **Typed endpoints** — frozen `Endpoint` constants with IDE autocomplete
- **Bearer auth** — JWT token caching, auto-refresh, 401 retry
- **API key auth** — header-based key injection
- **OData support** — key predicates, query parameters
- **Plugin system** — discovery-based adapters, no framework lock-in
- **Workspace management** — multi-API configs, variable storage
- **Workflow orchestration** — `@stage` decorator, `WorkflowContext`, sequential runner

## CLI Reference

```
restful workspace create -n NAME    # create workspace
restful workspace info              # show config
restful workspace vars set K V      # set variable
restful plugin list                 # list registered plugins
restful plugin validate             # validate plugin + source
restful plugin load                 # generate endpoint modules
restful workflow list               # list workflows
restful workflow run NAME           # run all stages
restful workflow run NAME --stage X # run single stage
```

## Documentation

Full docs at [joshuajerome.github.io/restful-sdk](https://joshuajerome.github.io/restful-sdk)

## About

restful-sdk is a Python library for structuring REST API calls into repeatable, type-safe workflows. It was built to solve the gap between ad-hoc scripts with hardcoded URLs and heavyweight API clients like Postman — giving you typed endpoints with IDE autocomplete, automatic token management, and composable workflow stages, all in plain Python.

The companion desktop app [Restful Notebooks](https://github.com/joshuajerome/restful-notebooks) provides a visual GUI for workspace management, endpoint browsing, request building, and notebook orchestration.

## License

MIT
