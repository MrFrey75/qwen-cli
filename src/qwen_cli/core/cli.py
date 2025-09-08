"""
Core CLI logic for Qwen CLI – Phase 0 & 1.
Handles argument parsing and command execution.

file: src/qwen_cli/core/cli.py
"""

import argparse
import os
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import List
from .config import QwenConfig
from qwen_cli.commands.ask import cmd_ask
from qwen_cli.commands.chat import cmd_chat
from qwen_cli.commands.config_cmd import cmd_config
from qwen_cli.commands.test_cmd import cmd_test
from qwen_cli.commands.gui import cmd_gui


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
  qwen chat                  Interactive chat session
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
    ask_parser.add_argument(
        "--model",
        default=os.environ.get("QWEN_MODEL", QwenConfig.load().model),
        help="Model to use (default: env QWEN_MODEL or 'qwen:latest')",
    )
    ask_parser.add_argument(
        "--host",
        default=os.environ.get("QWEN_OLLAMA_HOST", QwenConfig.load().host),
        help="Ollama host URL (default: env QWEN_OLLAMA_HOST or http://localhost:11434)",
    )
    ask_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-confirm prompts (e.g., model download)",
    )

    # `chat` command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat session")
    chat_parser.add_argument(
        "--model",
        default=os.environ.get("QWEN_MODEL", QwenConfig.load().model),
        help="Model to use (default: env QWEN_MODEL or 'qwen:latest')",
    )
    chat_parser.add_argument(
        "--host",
        default=os.environ.get("QWEN_OLLAMA_HOST", QwenConfig.load().host),
        help="Ollama host URL (default: env QWEN_OLLAMA_HOST or http://localhost:11434)",
    )
    chat_parser.add_argument(
        "--system",
        default=os.environ.get("QWEN_SYSTEM", QwenConfig.load().system_prompt),
        help="System prompt for the assistant",
    )
    chat_parser.add_argument(
        "--max-messages",
        type=int,
        default=int(os.environ.get("QWEN_MAX_MESSAGES", str(QwenConfig.load().max_messages))),
        help="Maximum number of recent messages to keep in memory (excluding system)",
    )
    chat_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-confirm prompts (e.g., model download)",
    )
    chat_parser.add_argument(
        "--no-log",
        action="store_true",
        help="Disable logging (by default chats are logged to ~/.qwen/history)",
    )
    chat_parser.add_argument(
        "--session",
        help="Load prior chat history from a JSONL file or session id (filename)",
    )
    chat_parser.add_argument(
        "--history-dir",
        default=os.environ.get("QWEN_HISTORY_DIR", QwenConfig.load().history_dir),
        help="Directory to store/read chat histories (default: ./logs)",
    )
    chat_parser.add_argument(
        "--title",
        default=os.environ.get("QWEN_SESSION_TITLE", QwenConfig.load().title),
        help="Optional session title used in the history filename",
    )

    # `config` command
    cfg_parser = subparsers.add_parser("config", help="Manage Qwen CLI configuration")
    cfg_sub = cfg_parser.add_subparsers(dest="config_cmd")
    cfg_sub.add_parser("path", help="Show config file path")
    cfg_get = cfg_sub.add_parser("get", help="Get a config value")
    cfg_get.add_argument("key", help="Config key, e.g. model, host, history_dir, max_messages, system_prompt, title")
    cfg_set = cfg_sub.add_parser("set", help="Set and save a config value")
    cfg_set.add_argument("key")
    cfg_set.add_argument("value")
    cfg_sub.add_parser("list", help="List all configuration values")

    # `test` command
    subparsers.add_parser("test", help="Run test suite (pytest -v)")

    # `gui` command
    subparsers.add_parser("gui", help="Launch experimental GUI (PyQt)")

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

    if not args:
        parser.print_help()
        return 0

    if parsed.command == "ask":
        cmd_ask(parsed)
        return 0
    if parsed.command == "chat":
        cmd_chat(parsed)
        return 0
    if parsed.command == "config":
        cmd_config(parsed)
        return 0
    if parsed.command == "test":
        return cmd_test(parsed)
    if parsed.command == "gui":
        return cmd_gui(parsed)

    # If no valid command, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())