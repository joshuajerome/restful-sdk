# Variables

Workspace variables are persistent key-value pairs shared across workflow stages and sessions.

## Usage

```python
# In a workflow stage
@stage("Extract data")
def extract(ctx: WorkflowContext):
    response = ctx.clients.sfm.get(instance_rest.BlueprintTemplates)
    templates = response.json()["BlueprintTemplate"]
    ctx.set("template_count", str(len(templates)))

@stage("Use data")
def use_data(ctx: WorkflowContext):
    count = ctx.get("template_count")
    print(f"Processing {count} templates")
```

## CLI

```bash
# Set a variable
python -m restful workspace vars set my_key my_value

# List all variables
python -m restful workspace vars list

# Delete a variable
python -m restful workspace vars delete my_key
```

## Storage

Variables are stored in `.restful/variables.json`:

```json
{
  "template_count": "12",
  "last_run": "2026-03-31"
}
```

All values are stored as strings. Variables persist across workflow runs and CLI sessions.

## Persistence

- `ctx.set()` updates the in-memory store
- After a workflow run completes, variables are saved to disk
- `workspace vars set` saves immediately
