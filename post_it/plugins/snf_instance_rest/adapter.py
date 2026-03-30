from __future__ import annotations

import json
from pathlib import Path

from post_it.models import EndpointSpec

# URL transform: /redfish/v1/SNF/... -> /redfish/v1/SFM/1/...
SNF_PREFIX = "/redfish/v1/SNF/"
SFM_PREFIX = "/redfish/v1/SFM/1/"

METHOD_KEYS = {
    "access-groups-for-get": "GET",
    "access-groups-for-post": "POST",
    "access-groups-for-put": "PUT",
    "access-groups-for-delete": "DELETE",
    "access-groups-for-patch": "PATCH",
}


def _url_to_name(url: str) -> str:
    """Convert a URL path to a PascalCase constant name."""
    suffix = url
    if suffix.startswith(SNF_PREFIX):
        suffix = suffix[len(SNF_PREFIX) :]
    elif suffix.startswith("/redfish/v2/SNF/"):
        suffix = "V2_" + suffix[len("/redfish/v2/SNF/") :]
    elif suffix.startswith("/redfish/v1/"):
        suffix = suffix[len("/redfish/v1/") :]

    parts = [p for p in suffix.split("/") if p]
    return "".join(parts)


def _transform_url(url: str) -> str:
    """Transform /redfish/v1/SNF/X -> /redfish/v1/SFM/1/X."""
    if url.startswith(SNF_PREFIX):
        return SFM_PREFIX + url[len(SNF_PREFIX) :]
    return url


def _extract_access_groups(entry: dict) -> dict[str, list[str]]:
    """Extract access group metadata from an rbac entry."""
    groups = {}
    for key in METHOD_KEYS:
        if key in entry:
            groups[key] = entry[key]
    return groups


class SnfInstanceRestAdapter:
    """Adapter for SFM's rbac_access_matrix.json format."""

    name = "snf-instance-rest"

    def parse(self, source: Path) -> list[EndpointSpec]:
        with source.open("r", encoding="utf-8") as f:
            data = json.load(f)

        entries = data.get("rbac", [])
        specs: list[EndpointSpec] = []
        seen_names: dict[str, int] = {}

        for entry in entries:
            url = entry["url"]
            methods = tuple(method for key, method in METHOD_KEYS.items() if key in entry)
            if not methods:
                continue

            path = _transform_url(url)
            name = _url_to_name(url)

            if name in seen_names:
                seen_names[name] += 1
                name = f"{name}_{seen_names[name]}"
            else:
                seen_names[name] = 0

            specs.append(
                EndpointSpec(
                    path=path,
                    methods=methods,
                    name=name,
                    metadata={"access_groups": _extract_access_groups(entry)},
                )
            )

        return specs
