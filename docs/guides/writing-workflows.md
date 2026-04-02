# Writing Workflows

Workflows are Python scripts in the `workflows/` directory with `@stage`-decorated functions.

## Basic Structure

```python
# workflows/my_flow.py
from restful import stage, WorkflowContext

@stage("Step 1 — Fetch")
def fetch(ctx: WorkflowContext):
    response = ctx.clients.sfm.get(instance_rest.BlueprintTemplates)
    templates = response.json()["BlueprintTemplate"]
    ctx.set("template_count", str(len(templates)))

@stage("Step 2 — Process")
def process(ctx: WorkflowContext):
    count = int(ctx.get("template_count"))
    if count > 0:
        # Create infrastructure
        ctx.clients.sfm.post(instance_rest.Infrastructures, payload={
            "Name": f"auto-infra-{count}",
        })
```

## Passing Data Between Stages

Use `ctx.set()` and `ctx.get()` to pass data:

```python
@stage("Extract")
def extract(ctx: WorkflowContext):
    response = ctx.clients.sfm.get(endpoint)
    ctx.set("infra_id", response.json()["Id"])

@stage("Use")
def use(ctx: WorkflowContext):
    infra_id = ctx.get("infra_id")
    ctx.clients.sfm.get(InfraDetails, params={"id": infra_id})
```

All variable values are strings. Variables persist to `.restful/variables.json` after the workflow completes.

## Using Multiple APIs

```python
@stage("Cross-API operation")
def cross_api(ctx: WorkflowContext):
    # SFM API
    nodes = ctx.clients.sfm.get(Nodes)

    # Netbox API
    devices = ctx.clients.netbox.get(Devices)
```

Each API configured in the workspace config is available as `ctx.clients.<alias>`.

## Running

```bash
# All stages sequentially
python -m restful workflow run my_flow

# Single stage (useful for development)
python -m restful workflow run my_flow --stage "Step 1 — Fetch"
```

## Tips

- Keep stages focused — one API operation per stage
- Use descriptive stage names that read as steps in a process
- Set variables for any data you need across stages
- Stages run in decorator order, top to bottom
