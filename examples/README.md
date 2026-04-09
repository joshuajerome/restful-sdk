# Examples

## basic_rest.py

Direct REST client usage without workspaces or workflows. Shows `Client`, `Endpoint`, OData params, query params, and POST requests.

```bash
python examples/basic_rest.py
```

## workflow_stages.py

Multi-stage workflow chaining REST calls. Fetches users → posts → comments with data flowing between stages via `WorkflowContext`.

```bash
python examples/workflow_stages.py
```

## workspace_setup.py

Programmatic workspace creation and configuration. Shows `create_workspace`, `WorkspaceConfig`, and `VariableStore`.

```bash
python examples/workspace_setup.py
```
