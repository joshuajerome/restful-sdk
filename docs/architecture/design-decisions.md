# Design Decisions

## Library First, CLI Second

restful is a Python library that happens to have a CLI. Users write `from restful import Client` in their scripts — they don't need the CLI to use it. The CLI is convenience for workspace management and workflow execution.

## Plugin-Driven Endpoint Ingestion

Rather than requiring a specific API format, restful uses a plugin system. Each plugin adapter knows how to parse one format and produce normalized `EndpointSpec` objects. This means adding support for a new API format never requires modifying core code.

## Code Generation Over Runtime Parsing

Endpoints are generated as Python source files, not parsed at runtime. This gives users:
- IDE autocomplete on every endpoint constant
- Import errors at startup (not runtime) if an endpoint is missing
- Zero overhead on import — no file parsing or API calls

## Workspace Discovery

Walking up from cwd to find `*.config.yaml` means users can run commands from any subdirectory. This matches how tools like git find `.git/`.

## File-Based Token Cache

Tokens are cached to a JSON file rather than an in-memory store or database. This means:
- Tokens persist across process restarts
- Multiple scripts can share the same cached token
- No daemon process needed

## Variables as Strings

All variable values are strings. This simplifies serialization and avoids type confusion when passing data between stages. Users parse to the type they need.

## No Docker Dependency

restful is a pure Python library with no container runtime dependency. Unlike CUTIP (which orchestrates containers), restful focuses entirely on REST API automation.
