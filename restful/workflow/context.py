"""WorkflowContext — shared state passed to @stage functions."""

from __future__ import annotations

import os
from typing import Any

from restful.auth.bearer import BearerAuth
from restful.client import Client
from restful.workspace.config import ApiConnection, WorkspaceConfig
from restful.workspace.variables import VariableStore


class ClientNamespace:
    """
    Attribute-access namespace for API clients.

    Usage:
        ctx.clients.sfm.get(...)
        ctx.clients.mon.post(...)
    """

    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}

    def _add(self, alias: str, client: Client) -> None:
        self._clients[alias] = client

    def __getattr__(self, name: str) -> Client:
        if name.startswith("_"):
            raise AttributeError(name)
        client = self._clients.get(name)
        if client is None:
            available = ", ".join(sorted(self._clients.keys())) or "(none)"
            raise AttributeError(f"No API client '{name}'. Available: {available}")
        return client

    def __repr__(self) -> str:
        return f"ClientNamespace({list(self._clients.keys())})"


def _build_client(api: ApiConnection) -> Client:
    """Build a Client from an ApiConnection config."""
    base_url = api.base_url
    auth = None

    if api.auth.type == "bearer":
        password = os.environ.get(api.auth.password_env, "") if api.auth.password_env else ""
        auth = BearerAuth(
            base_url=base_url,
            login_path=api.auth.login_path,
            payload={"username": api.auth.username, "password": password},
        )
    elif api.auth.type == "apikey":
        # API key auth is handled by adding a header — use a simple lambda-based strategy
        key = os.environ.get(api.auth.key_env, "") if api.auth.key_env else ""
        if key:
            from restful.auth.base import AuthStrategy

            class ApiKeyAuth:
                def auth_headers(self):
                    return {api.auth.header: key}

                def invalidate(self):
                    pass

            auth = ApiKeyAuth()

    return Client(base_url=base_url, auth=auth)


class WorkflowContext:
    """
    Shared context passed to @stage functions.

    Provides:
        ctx.clients.<alias> — pre-configured Client per API
        ctx.get(key) — read a workspace variable
        ctx.set(key, value) — write a workspace variable
        ctx.all_vars() — all current variables
    """

    def __init__(
        self,
        clients: ClientNamespace | None = None,
        variables: VariableStore | None = None,
    ):
        self.clients = clients or ClientNamespace()
        self._variables = variables

    def get(self, key: str) -> str | None:
        """Read a workspace variable."""
        if self._variables is None:
            return None
        return self._variables.get(key)

    def set(self, key: str, value: Any) -> None:
        """Write a workspace variable."""
        if self._variables is None:
            raise RuntimeError("No variable store available (running outside a workspace?)")
        self._variables.set(key, value)

    def all_vars(self) -> dict[str, str]:
        """Return all current variables."""
        if self._variables is None:
            return {}
        return self._variables.all()

    @classmethod
    def from_workspace(cls, config: WorkspaceConfig) -> WorkflowContext:
        """Build a WorkflowContext from a workspace config."""
        clients = ClientNamespace()
        for api in config.apis:
            client = _build_client(api)
            clients._add(api.alias, client)

        variables = VariableStore(config.root)
        return cls(clients=clients, variables=variables)
