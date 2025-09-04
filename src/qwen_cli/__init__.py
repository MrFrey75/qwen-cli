#!/usr/bin/env python3
"""
Core CLI logic for Qwen CLI – Phase 0.
Handles argument parsing and command execution.
"""

import argparse
import sys
from typing import List


def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="qwen",
        description="Qwen CLI – A secure, local AI assistant powered by Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qwen --help                Show this help message
  qwen --version             Show version info
        """.strip(),
    )
    parser.add_argument(
        "--version",
        action="version",
        version="qwen-cli 0.1.0",
        help="Show version and exit.",
    )
    return parser


def main(args: List[str] = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 on success)
    """
    if args is None:
        args = sys.argv[1:]

    parser = create_parser()
    parsed = parser.parse_args(args)

    # If no args provided, show help
    if not args:
        parser.print_help()
        return 0

    # Argument parsing automatically handles --version
    # If we get here and no other action was taken, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())