# src/qwen_cli/core/cli.py
"""
Core CLI logic for Qwen CLI – Phase 0 & 1.
Handles argument parsing and command execution.
"""

import argparse
import sys
from typing import List
from .ollama import OllamaInterface  # Relative import


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the Qwen CLI."""
    parser = argparse.ArgumentParser(
        prog="qwen",
        description="Qwen CLI – A secure, local AI assistant powered by Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qwen --help                Show this help message
  qwen --version             Show version info
  qwen ask "What is Python?" Ask Qwen a question
        """.strip(),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="qwen-cli 0.1.0",
        help="Show version and exit.",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # `ask` command
    ask_parser = subparsers.add_parser("ask", help="Ask Qwen a question")
    ask_parser.add_argument("prompt", help="The question or prompt to send to Qwen")

    return parser


def cmd_ask(args):
    """Handle `qwen ask "prompt"` command."""
    ollama = OllamaInterface()

    if not ollama.is_ollama_running():
        print("❌ Ollama is not running.")
        print("Please start Ollama: https://ollama.com")
        sys.exit(1)

    model = "qwen:latest"
    if model not in ollama.list_models():
        print(f"❌ Model '{model}' not found.")
        confirm = input(f"👉 Would you like to pull '{model}'? (y/N): ")
        if confirm.lower() != "y":
            print("❌ Cannot proceed without model.")
            sys.exit(1)
        if not ollama.pull_model(model):
            sys.exit(1)

    print(f"\n🤖 Qwen: ", end="", flush=True)
    try:
        for chunk in ollama.generate(model, args.prompt):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
        sys.exit(1)
    finally:
        print()  # Newline at end


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

    if not args:
        parser.print_help()
        return 0

    if parsed.command == "ask":
        cmd_ask(parsed)
        return 0

    # If no valid command, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())