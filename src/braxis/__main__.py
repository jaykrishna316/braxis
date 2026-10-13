"""Braxis CLI entry point with MCP server mode."""

import argparse
import sys

from src.braxis.mcp_stdio import run_server


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Braxis - AI Context Platform for Python Projects"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # MCP server command
    mcp_parser = subparsers.add_parser("mcp", help="Run MCP server (for Claude)")
    mcp_parser.set_defaults(func=run_mcp_server)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func()
    else:
        parser.print_help()


def run_mcp_server():
    """Run the MCP server."""
    try:
        run_server()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
