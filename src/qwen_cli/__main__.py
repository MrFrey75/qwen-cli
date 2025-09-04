#!/usr/bin/env python3
"""
Entry point for the Qwen CLI.
"""

import sys
from qwen_cli.core.cli import main as cli_main


def main():
    """Main function to run the CLI."""
    sys.exit(cli_main())


if __name__ == "__main__":
    main()