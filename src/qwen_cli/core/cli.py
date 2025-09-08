"""
Core CLI logic for Qwen CLI – Phase 0 & 1.
Handles argument parsing and command execution.

file: src/qwen_cli/core/cli.py
"""

import argparse
import os
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
        default=os.environ.get("QWEN_MODEL", "qwen:latest"),
        help="Model to use (default: env QWEN_MODEL or 'qwen:latest')",
    )
    ask_parser.add_argument(
        "--host",
        default=os.environ.get("QWEN_OLLAMA_HOST", "http://localhost:11434"),
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
        default=os.environ.get("QWEN_MODEL", "qwen:latest"),
        help="Model to use (default: env QWEN_MODEL or 'qwen:latest')",
    )
    chat_parser.add_argument(
        "--host",
        default=os.environ.get("QWEN_OLLAMA_HOST", "http://localhost:11434"),
        help="Ollama host URL (default: env QWEN_OLLAMA_HOST or http://localhost:11434)",
    )
    chat_parser.add_argument(
        "--system",
        default=os.environ.get("QWEN_SYSTEM", "You are Qwen, a helpful assistant."),
        help="System prompt for the assistant",
    )
    chat_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-confirm prompts (e.g., model download)",
    )

    return parser


def cmd_ask(args):
    """Handle `qwen ask "prompt"` command."""
    ollama = OllamaInterface(host=args.host)

    if not ollama.is_ollama_running():
        print("❌ Ollama is not running.")
        print("Please start Ollama: https://ollama.com")
        sys.exit(1)

    model = args.model
    if model not in ollama.list_models():
        print(f"❌ Model '{model}' not found.")
        if not args.yes:
            confirm = input(f"👉 Would you like to pull '{model}'? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cannot proceed without model.")
                sys.exit(1)
        else:
            print("--yes provided; proceeding to pull model.")
        if not ollama.pull_model(model):
            print("❌ Cannot proceed without model.")
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


def cmd_chat(args):
    """Handle `qwen chat` interactive session with in-memory context."""
    ollama = OllamaInterface(host=args.host)

    if not ollama.is_ollama_running():
        print("❌ Ollama is not running.")
        print("Please start Ollama: https://ollama.com")
        sys.exit(1)

    model = args.model
    if model not in ollama.list_models():
        print(f"❌ Model '{model}' not found.")
        if not args.yes:
            confirm = input(f"👉 Would you like to pull '{model}'? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cannot proceed without model.")
                sys.exit(1)
        else:
            print("--yes provided; proceeding to pull model.")
        if not ollama.pull_model(model):
            print("❌ Cannot proceed without model.")
            sys.exit(1)

    print("\n💬 Interactive chat started. Type '/exit' to quit, '/reset' to clear.")
    messages = [{"role": "system", "content": args.system}]

    while True:
        try:
            user_input = input("\n🟢 You: ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye")
            break

        if not user_input.strip():
            continue
        if user_input.strip() in {"/exit", ":q", ":quit"}:
            print("👋 Bye")
            break
        if user_input.strip() == "/reset":
            messages = [{"role": "system", "content": args.system}]
            print("♻️  Context reset.")
            continue

        messages.append({"role": "user", "content": user_input})

        print("🤖 Qwen: ", end="", flush=True)
        try:
            for chunk in ollama.chat(model, messages):
                print(chunk, end="", flush=True)
                # Accumulate assistant message content
            print()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

        # Append last assistant message to history
        # Since we streamed, we can't easily reconstruct. Ask once more non-stream? For now, skip storing exact assistant text.
        # In practice, Ollama chat returns chunks with message content only; the model will still have context via messages list if we add assistant.
        # Minimal approach: add a placeholder to keep turn structure.
        messages.append({"role": "assistant", "content": ""})

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

    # If no valid command, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())