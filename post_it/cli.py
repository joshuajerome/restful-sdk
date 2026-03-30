from __future__ import annotations

import argparse
import sys
from pathlib import Path

from post_it.config import PostItConfig
from post_it.generator.python_module import generate
from post_it.plugins import registry


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate typed endpoints file from plugin + source."""
    config = PostItConfig.load(Path(args.config))
    adapter = registry.get(config.plugin)
    if not adapter:
        print(f"Error: Unknown plugin '{config.plugin}'")
        print(f"Available plugins: {', '.join(registry.list_plugins())}")
        sys.exit(1)

    source = Path(config.source)
    if not source.exists():
        print(f"Error: Source file not found: {source}")
        sys.exit(1)

    specs = adapter.parse(source)
    source_code = generate(specs, plugin_name=config.plugin)

    output = Path(config.endpoints)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source_code, encoding="utf-8")
    print(f"Generated {output} ({len(specs)} endpoints)")


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate post-it.yaml and source file."""
    try:
        config = PostItConfig.load(Path(args.config))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing config: {e}")
        sys.exit(1)

    adapter = registry.get(config.plugin)
    if not adapter:
        print(f"Error: Unknown plugin '{config.plugin}'")
        print(f"Available plugins: {', '.join(registry.list_plugins())}")
        sys.exit(1)

    source = Path(config.source)
    if not source.exists():
        print(f"Error: Source file not found: {source}")
        sys.exit(1)

    try:
        specs = adapter.parse(source)
    except Exception as e:
        print(f"Error parsing source: {e}")
        sys.exit(1)

    print(f"Valid. Plugin: {config.plugin}, Source: {config.source}, Endpoints: {len(specs)}")


def cmd_plugins(args: argparse.Namespace) -> None:
    """List available plugins."""
    plugins = registry.list_plugins()
    if not plugins:
        print("No plugins registered.")
        return
    for name in plugins:
        print(f"  {name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="post-it",
        description="Ingest API endpoints, generate typed Python modules",
    )

    sub = parser.add_subparsers(dest="command")

    # Shared config argument for commands that need it
    config_arg = argparse.ArgumentParser(add_help=False)
    config_arg.add_argument(
        "-c",
        "--config",
        default="post-it.yaml",
        help="Path to config file (default: post-it.yaml)",
    )

    sub.add_parser("generate", parents=[config_arg], help="Generate typed endpoints file")
    sub.add_parser("validate", parents=[config_arg], help="Validate config and source file")
    sub.add_parser("plugins", help="List available plugins")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "plugins":
        cmd_plugins(args)
    else:
        parser.print_help()
        sys.exit(1)
