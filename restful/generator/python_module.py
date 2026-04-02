from __future__ import annotations

from restful.models import EndpointSpec


def _escape(s: str) -> str:
    """Escape a string for safe inclusion in Python source."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate(specs: list[EndpointSpec], plugin_name: str = "") -> str:
    """Generate Python source with Endpoint constants from EndpointSpecs."""
    header_parts = [
        '"""',
        "Auto-generated endpoint constants.",
    ]
    if plugin_name:
        header_parts.append(f"Plugin: {plugin_name}")
    header_parts.extend(
        [
            f"Endpoints: {len(specs)}",
            "DO NOT EDIT — regenerate with: python -m restful generate",
            '"""',
            "",
            "from restful.models import Endpoint",
            "",
        ]
    )

    lines = list(header_parts)
    for spec in specs:
        methods_str = ", ".join(f'"{m}"' for m in spec.methods)
        safe_path = _escape(spec.path)
        lines.append(f'{spec.name} = Endpoint(path="{safe_path}", methods=({methods_str},))')

    lines.append("")
    return "\n".join(lines)
