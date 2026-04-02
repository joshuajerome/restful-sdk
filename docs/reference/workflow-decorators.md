# Workflow Decorators

## @stage

Registers a function as a named workflow stage.

```python
from restful import stage

@stage("Fetch data")
def fetch_data(ctx):
    ...
```

**Signature:** `stage(name: str) -> Callable`

- Attaches `_stage_name` and `_stage_order` attributes to the function
- Registers the function in a global stage registry
- Functions work identically with or without the decorator

## WorkflowContext

```python
from restful import WorkflowContext
```

| Method | Description |
|--------|-------------|
| `ctx.clients.<alias>` | Access pre-configured Client by API alias |
| `ctx.get(key)` | Read a variable (returns `None` if missing) |
| `ctx.set(key, value)` | Set a variable (string value) |
| `ctx.all_vars()` | Return all variables as `dict[str, str]` |

### Building from Workspace

```python
ctx = WorkflowContext.from_workspace(config)
```

Builds a `ClientNamespace` with one Client per API in the workspace config, plus a `VariableStore` loaded from `.restful/variables.json`.

## StageResult

Returned by `WorkflowRunner.run()` and `run_stage()`:

| Field | Type | Description |
|-------|------|-------------|
| `stage_name` | `str` | Name of the stage |
| `success` | `bool` | Whether the stage completed without error |
| `return_value` | `Any` | Return value from the stage function |
| `error` | `str \| None` | Error message if failed |
| `duration_ms` | `int` | Execution time in milliseconds |
| `captured_vars` | `dict[str, str]` | Variables set during this stage |
