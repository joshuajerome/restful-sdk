# Concepts Overview

restful is organized around five core concepts:

## Workspace

A directory with a `*.config.yaml` marker file. Contains API configurations, generated endpoint modules, workflow scripts, and runtime state (token cache, variables).

[Learn more →](workspaces.md)

## Plugin

An adapter that parses an API specification (RBAC JSON, OpenAPI, custom format) and produces a normalized list of `EndpointSpec` objects. These are then code-generated into importable Python modules.

[Learn more →](plugins-endpoints.md)

## Client

A REST client that takes typed `Endpoint` objects and makes HTTP calls. Handles authentication, OData key predicates, query parameters, and automatic 401 retry.

## Workflow

A Python script with `@stage`-decorated functions. A `WorkflowContext` provides pre-configured clients (one per API) and a shared variable store. The workflow runner executes stages sequentially.

[Learn more →](workflows.md)

## Authentication

Bearer token auth with file-based caching, JWT expiry detection, and automatic refresh. API key auth via header injection. Both configured per-API in the workspace config.

[Learn more →](authentication.md)
