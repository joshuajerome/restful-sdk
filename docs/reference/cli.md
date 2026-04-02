# CLI Reference

All commands are invoked via `python -m restful <command>`.

## Workspace Commands

### `workspace create`

Create a new workspace directory with scaffold files.

```bash
python -m restful workspace create -n my-project
```

Creates: config template, `__main__.py`, `apis/`, `workflows/`, `.restful/`, `.gitignore`.

### `workspace info`

Display current workspace configuration and API connections.

```bash
python -m restful workspace info
```

### `workspace vars set`

Set a workspace variable.

```bash
python -m restful workspace vars set KEY VALUE
```

### `workspace vars list`

List all workspace variables. Values longer than 60 characters are truncated.

```bash
python -m restful workspace vars list
```

### `workspace vars delete`

Delete a workspace variable.

```bash
python -m restful workspace vars delete KEY
```

## Plugin Commands

### `plugin list`

List all available plugins (built-in and registered).

```bash
python -m restful plugin list
```

### `plugin validate`

Validate plugin configuration and source files without generating code.

```bash
python -m restful plugin validate          # all APIs
python -m restful plugin validate -n sfm   # specific API by alias
```

### `plugin load`

Parse source files and generate endpoint modules.

```bash
python -m restful plugin load              # all APIs
python -m restful plugin load -n sfm       # specific API by alias
```

Output: `apis/<sanitized_name>/endpoints.py`

## Workflow Commands

### `workflow list`

List all workflow files in the `workflows/` directory.

```bash
python -m restful workflow list
```

### `workflow run`

Run a workflow or individual stage.

```bash
python -m restful workflow run my_flow                    # all stages
python -m restful workflow run my_flow --stage "Fetch"    # single stage
python -m restful workflow run my_flow --list             # list stages only
```
