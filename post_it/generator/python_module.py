from __future__ import annotations

from post_it.models import EndpointSpec


def generate(specs: list[EndpointSpec], plugin_name: str = "") -> str:
    """Generate Python source with Endpoint constants from EndpointSpecs."""
    lines = [
        '"""',
        "Auto-generated endpoint constants.",
        "",
        f"Plugin: {plugin_name}" if plugin_name else "",
        f"Endpoints: {len(specs)}",
        "DO NOT EDIT — regenerate with: python -m post_it generate",
        '"""',
        "",
        "from post_it.models import Endpoint",
        "",
    ]

    # Remove empty lines from header
    lines = [line for line in lines if line != "" or lines[lines.index(line) - 1] != ""]

    for spec in specs:
        methods_str = ", ".join(f'"{m}"' for m in spec.methods)
        lines.append(f'{spec.name} = Endpoint(path="{spec.path}", methods=({methods_str},))')

    lines.append("")
    return "\n".join(lines)
