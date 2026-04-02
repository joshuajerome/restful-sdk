# restful

**REST workflow automation framework** — ingest API endpoint definitions, generate typed Python modules, and orchestrate multi-step REST workflows.

## What is restful?

restful is a Python tool that structures REST API calls into repeatable, type-safe workflows. Instead of writing ad-hoc scripts with hardcoded URLs and manual token management, restful gives you:

- **Typed endpoints** — every API endpoint is a frozen Python constant with IDE autocomplete
- **Automatic authentication** — bearer tokens cached to disk, auto-refreshed on expiry, 401 retry built-in
- **Plugin-driven ingestion** — parse API specs (RBAC matrices, OpenAPI, custom formats) into typed endpoint modules
- **Workspace management** — configure multiple APIs, variables, and credentials in a single `*.config.yaml`
- **Workflow orchestration** — chain REST calls into `@stage`-decorated Python functions with shared context

## Quick Example

```python
from restful import Client, BearerAuth, stage, WorkflowContext

@stage("Fetch blueprints")
def fetch_blueprints(ctx: WorkflowContext):
    response = ctx.clients.sfm.get(instance_rest.BlueprintTemplates)
    templates = response.json()["BlueprintTemplate"]
    ctx.set("template_count", str(len(templates)))

@stage("Create infrastructure")
def create_infra(ctx: WorkflowContext):
    ctx.clients.sfm.post(instance_rest.Infrastructures, payload={
        "Name": "my-infra",
        "TemplateName": "default",
    })
```

## Design Principles

1. **Library first** — restful is a Python library. Users write scripts, not config files.
2. **No CLI required** — `python my_script.py` works. The CLI is convenience, not a requirement.
3. **Transparent caching** — tokens cached to `~/.restful/cache.json`. Users never manage tokens.
4. **Plugin ecosystem** — new API formats are supported by writing a small adapter, not modifying core code.

## Getting Started

- [Installation](getting-started/installation.md) — install from GitHub releases
- [Quickstart](getting-started/quickstart.md) — create a workspace and make your first request
- [Workspace Layout](getting-started/workspace-layout.md) — understand the directory structure
