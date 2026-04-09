# Workflows

Workflows are Python scripts that chain REST calls into sequential stages with shared context. Workflow files live in the `notebooks/` directory of a workspace.

## Stage Decorator

The `@stage` decorator registers a function as a named workflow step:

```python
from restful import stage, WorkflowContext

@stage("Fetch data")
def fetch_data(ctx: WorkflowContext):
    response = ctx.clients.sfm.get(instance_rest.BlueprintTemplates)
    ctx.set("count", str(len(response.json()["items"])))

@stage("Report results")
def report(ctx: WorkflowContext):
    print(f"Found {ctx.get('count')} items")
```

Functions work with or without the decorator — `@stage` only registers them for the runner.

## WorkflowContext

Every stage receives a `WorkflowContext` with:

- **`ctx.clients.<alias>`** — pre-configured Client instances for each API in the workspace
- **`ctx.get(key)`** — read a workspace variable
- **`ctx.set(key, value)`** — write a workspace variable (persisted to disk after the run)
- **`ctx.all_vars()`** — all current variables

## Running Workflows

```bash
# Run all stages
python -m restful workflow run my_flow

# Run a single stage
python -m restful workflow run my_flow --stage "Fetch data"

# List stages
python -m restful workflow run my_flow --list
```

## Stage Results

Each stage returns a `StageResult`:

```
[✓] Fetch data (245ms)
    count = 12
[✓] Report results (3ms)
```

Results include: success/failure, duration, captured variables, error message (on failure).

## Execution

Stages run sequentially in decorator order. If a stage fails, execution stops. Variables are persisted to `.restful/variables.json` after the run completes. Workflow files are discovered from the `notebooks/` directory.
