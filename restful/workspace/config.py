"""Parse <name>.config.yaml into WorkspaceConfig."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


def _sanitize_name(name: str) -> str:
    """Convert a name to a valid Python identifier: trim, lowercase, replace hyphens/spaces with underscores."""
    s = name.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s or "unnamed"


@dataclass(frozen=True)
class AuthConfig:
    type: str = "none"  # "bearer" | "apikey" | "none"
    login_path: str = ""
    username: str = ""
    password_env: str = ""  # env var name for password
    header: str = "X-API-Key"
    key_env: str = ""  # env var name for API key

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> AuthConfig:
        if not data:
            return cls()
        return cls(
            type=data.get("type", "none"),
            login_path=data.get("login_path", ""),
            username=data.get("username", ""),
            password_env=data.get("password_env", ""),
            header=data.get("header", "X-API-Key"),
            key_env=data.get("key_env", ""),
        )


@dataclass(frozen=True)
class ApiConnection:
    name: str
    alias: str  # sanitized, used as ctx.clients.<alias>
    plugin: str
    source: str  # relative to workspace root
    base_url: str = ""  # API base URL (e.g. https://100.94.115.90)
    plugin_path: str = ""  # for custom plugins, relative to workspace root
    auth: AuthConfig = field(default_factory=AuthConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApiConnection:
        name = data.get("name", "")
        if not name:
            raise ValueError("API connection missing 'name' field")
        alias = data.get("alias") or _sanitize_name(name)
        plugin = data.get("plugin", "")
        source = data.get("source", "")
        return cls(
            name=name,
            alias=alias,
            plugin=plugin,
            source=source,
            base_url=data.get("base_url", ""),
            plugin_path=data.get("plugin_path", ""),
            auth=AuthConfig.from_dict(data.get("auth")),
        )


@dataclass
class WorkspaceConfig:
    name: str
    apis: list[ApiConnection]
    root: Path  # workspace root directory
    config_path: Path  # path to the config file

    @classmethod
    def load(cls, config_path: Path) -> WorkspaceConfig:
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Config must be a YAML mapping, got {type(data).__name__}")

        # Validate apiVersion
        api_version = data.get("apiVersion", "")
        if api_version and not api_version.startswith(("restful/", "post-it/")):
            raise ValueError(f"Unknown apiVersion: {api_version}")

        ws_data = data.get("workspace", {})
        if not isinstance(ws_data, dict):
            raise ValueError("'workspace' must be a mapping")

        ws_name = ws_data.get("name", config_path.stem.replace(".config", ""))

        apis_data = data.get("apis", [])
        if not isinstance(apis_data, list):
            raise ValueError("'apis' must be a list")

        apis = [ApiConnection.from_dict(a) for a in apis_data]

        # Validate unique aliases
        aliases = [a.alias for a in apis]
        dupes = [a for a in aliases if aliases.count(a) > 1]
        if dupes:
            raise ValueError(f"Duplicate API aliases: {', '.join(set(dupes))}")

        return cls(
            name=ws_name,
            apis=apis,
            root=config_path.parent,
            config_path=config_path,
        )

    def get_api(self, name_or_alias: str) -> ApiConnection | None:
        """Find an API by name or alias."""
        for api in self.apis:
            if api.name == name_or_alias or api.alias == name_or_alias:
                return api
        return None
