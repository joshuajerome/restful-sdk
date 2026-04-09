"""OpenAPI 3.x endpoint adapter — parses openapi.json/yaml into endpoint specs."""

import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

name = "openapi"


class EndpointSpec:
    """Endpoint specification produced by plugin adapters."""

    __slots__ = ("path", "methods", "name", "description", "metadata")

    def __init__(
        self,
        path: str,
        methods: tuple,
        name: str,
        description: str = "",
        metadata: dict = None,
    ):
        self.path = path
        self.methods = methods
        self.name = name
        self.description = description
        self.metadata = metadata if metadata is not None else {}


def _path_to_name(path: str) -> str:
    """Convert /api/v1/users/{id}/posts to UsersIdPosts (PascalCase)."""
    # Remove leading /api/vN prefix
    cleaned = re.sub(r"^/api/v\d+/", "/", path)
    # Split on / and {param}
    parts = []
    for segment in cleaned.strip("/").split("/"):
        if segment.startswith("{") and segment.endswith("}"):
            # Parameter — include as capitalized name
            parts.append(segment[1:-1].capitalize())
        elif segment:
            # Regular segment — capitalize first letter
            parts.append(segment[0].upper() + segment[1:] if segment else "")
    return "".join(parts) or "Root"


def _load_spec(source: Path) -> dict:
    """Load OpenAPI spec from JSON or YAML file."""
    text = source.read_text(encoding="utf-8")

    if source.suffix in (".yaml", ".yml"):
        try:
            import yaml

            return yaml.safe_load(text)
        except ImportError:
            raise ImportError("PyYAML is required to parse YAML OpenAPI specs. Install with: pip install pyyaml")
    else:
        return json.loads(text)


def parse(source: Path) -> list[EndpointSpec]:
    """Parse an OpenAPI 3.x spec file and return endpoint specs."""
    data = _load_spec(source)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON/YAML object in {source}, got {type(data).__name__}")

    # Validate it's OpenAPI
    openapi_version = data.get("openapi", "")
    if not openapi_version.startswith("3."):
        swagger = data.get("swagger", "")
        if not swagger:
            raise ValueError(f"Not an OpenAPI spec: missing 'openapi' or 'swagger' field in {source}")
        logger.warning("Swagger 2.x detected — parsing with limited support")

    paths = data.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError(f"'paths' must be an object in {source}")

    specs: list[EndpointSpec] = []
    seen_names: dict[str, int] = {}

    http_methods = {"get", "post", "put", "delete", "patch", "head", "options"}

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        methods = []
        description = ""
        tags: list[str] = []
        metadata: dict[str, Any] = {}

        for method in http_methods:
            if method in path_item:
                methods.append(method.upper())
                op = path_item[method]
                if isinstance(op, dict):
                    if not description:
                        description = op.get("summary", "") or op.get("description", "")
                    if not tags and "tags" in op:
                        tags = op["tags"]
                    # Collect parameters
                    params = op.get("parameters", [])
                    if params:
                        for p in params:
                            if isinstance(p, dict):
                                metadata.setdefault("parameters", []).append(
                                    {"name": p.get("name"), "in": p.get("in"), "required": p.get("required", False)}
                                )

        if not methods:
            continue

        ep_name = _path_to_name(path)

        # Handle duplicates
        if ep_name in seen_names:
            seen_names[ep_name] += 1
            ep_name = f"{ep_name}_{seen_names[ep_name]}"
        else:
            seen_names[ep_name] = 0

        if tags:
            metadata["tags"] = tags

        specs.append(
            EndpointSpec(
                path=path,
                methods=tuple(sorted(methods)),
                name=ep_name,
                description=description[:200] if description else "",
                metadata=metadata,
            )
        )

    return specs
