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
from .ollama import OllamaInterface  # Relative import
from .logger import get_logger


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
        default=os.environ.get(
            "QWEN_SYSTEM",
            (
                "You are Qwen, a helpful assistant. Always use the conversation history to answer. "
                "If the user has provided personal details (like name) earlier in this session, "
                "use them when helpful. Keep answers concise."
            ),
        ),
        help="System prompt for the assistant",
    )
    chat_parser.add_argument(
        "--max-messages",
        type=int,
        default=int(os.environ.get("QWEN_MAX_MESSAGES", "20")),
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
        default=os.environ.get("QWEN_HISTORY_DIR", str(Path.cwd() / "logs")),
        help="Directory to store/read chat histories (default: ./logs)",
    )
    chat_parser.add_argument(
        "--title",
        default=os.environ.get("QWEN_SESSION_TITLE", "session"),
        help="Optional session title used in the history filename",
    )

    return parser


def cmd_ask(args):
    """Handle `qwen ask "prompt"` command."""
    log = get_logger("qwen.cli")
    ollama = OllamaInterface(host=args.host)

    if not ollama.is_ollama_running():
        print("❌ Ollama is not running.")
        log.error("Ollama not running at %s", args.host)
        print("Please start Ollama: https://ollama.com")
        sys.exit(1)

    model = args.model
    if model not in ollama.list_models():
        print(f"❌ Model '{model}' not found.")
        log.info("Model not found: %s", model)
        if not args.yes:
            confirm = input(f"👉 Would you like to pull '{model}'? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cannot proceed without model.")
                sys.exit(1)
        else:
            print("--yes provided; proceeding to pull model.")
            log.info("Auto-pulling model %s", model)
        if not ollama.pull_model(model):
            print("❌ Cannot proceed without model.")
            log.error("Model pull failed: %s", model)
            sys.exit(1)

    print(f"\n🤖 Qwen: ", end="", flush=True)
    try:
        for chunk in ollama.generate(model, args.prompt):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
        log.exception("Generation error for model %s", model)
        sys.exit(1)
    finally:
        print()  # Newline at end


def cmd_chat(args):
    """Handle `qwen chat` interactive session with in-memory context."""
    log = get_logger("qwen.chat")
    ollama = OllamaInterface(host=args.host)

    if not ollama.is_ollama_running():
        print("❌ Ollama is not running.")
        log.error("Ollama not running at %s", args.host)
        print("Please start Ollama: https://ollama.com")
        sys.exit(1)

    model = args.model
    if model not in ollama.list_models():
        print(f"❌ Model '{model}' not found.")
        log.info("Model not found: %s", model)
        if not args.yes:
            confirm = input(f"👉 Would you like to pull '{model}'? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cannot proceed without model.")
                sys.exit(1)
        else:
            print("--yes provided; proceeding to pull model.")
            log.info("Auto-pulling model %s", model)
        if not ollama.pull_model(model):
            print("❌ Cannot proceed without model.")
            log.error("Model pull failed: %s", model)
            sys.exit(1)

    print("\n💬 Interactive chat started. Type '/exit' to quit, '/reset' to clear.")
    log.info("Chat started: model=%s host=%s", model, args.host)
    messages = [{"role": "system", "content": args.system}]
    session_facts = {}

    # Prepare logging and/or preloading
    history_dir = Path(args.history_dir)
    history_dir.mkdir(parents=True, exist_ok=True)
    log_fp = None
    log_path = None

    # Load prior session if provided
    if args.session:
        candidate = Path(args.session)
        if not candidate.exists():
            candidate = history_dir / (args.session if args.session.endswith(".jsonl") else f"{args.session}.jsonl")
        if candidate.exists():
            try:
                with candidate.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            role = obj.get("role")
                            content = obj.get("content")
                            if role in {"system", "user", "assistant"} and isinstance(content, str):
                                messages.append({"role": role, "content": content})
                        except Exception:
                            continue
                print(f"📜 Loaded history: {candidate}")
            except Exception as e:
                print(f"⚠️  Could not load session history: {e}")
        else:
            print(f"⚠️  Session not found: {candidate}")

    # Start log file if enabled
    if not args.no_log:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # Sanitize title for filename
        safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in (args.title or "session")).strip("-") or "session"
        log_path = history_dir / f"{safe_title}-{timestamp}.jsonl"
        try:
            log_fp = log_path.open("a", encoding="utf-8")
            # Log initial system prompt
            log_fp.write(json.dumps({"role": "system", "content": args.system}) + "\n")
            log_fp.flush()
            print(f"📝 Logging to: {log_path}")
        except Exception as e:
            print(f"⚠️  Could not open log file: {e}")
            log_fp = None

    while True:
        try:
            user_input = input("\n🟢 You: ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye")
            log.info("Chat ended via signal")
            break

        if not user_input.strip():
            continue
        if user_input.strip() in {"/exit", ":q", ":quit"}:
            print("👋 Bye")
            log.info("Chat ended by user")
            break
        if user_input.strip() == "/reset":
            messages = [{"role": "system", "content": args.system}]
            print("♻️  Context reset.")
            log.info("Context reset by user")
            continue

        # Lightweight fact extraction (in-memory only)
        text_lower = user_input.strip().lower()
        import re as _re
        m = _re.search(r"\bmy\s+name\s+is\s+([a-zA-Z][a-zA-Z\-']*)", text_lower)
        if m:
            # Store the canonical-cased version using original span when possible
            start, end = m.span(1)
            captured = user_input[start:end]
            session_facts["name"] = captured.strip()
            log.debug("Captured user name: %s", session_facts["name"])

        messages.append({"role": "user", "content": user_input})
        if log_fp is not None:
            try:
                log_fp.write(json.dumps({"role": "user", "content": user_input}) + "\n")
                log_fp.flush()
            except Exception:
                pass

        print("🤖 Qwen: ", end="", flush=True)
        try:
            assistant_content = ""
            # Build augmented messages including session facts so model leverages context
            augmented = [messages[0]]  # base system prompt
            if session_facts:
                facts_lines = []
                if "name" in session_facts:
                    facts_lines.append(f"User name: {session_facts['name']}")
                if facts_lines:
                    augmented.append({
                        "role": "system",
                        "content": "Known session facts about the user (use when relevant):\n- " + "\n- ".join(facts_lines),
                    })
            augmented.extend(messages[1:])

            for chunk in ollama.chat(model, augmented):
                assistant_content += chunk
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            log.exception("Chat error")
            continue

        # Append last assistant message to history
        messages.append({"role": "assistant", "content": assistant_content})
        if log_fp is not None:
            try:
                log_fp.write(json.dumps({"role": "assistant", "content": assistant_content}) + "\n")
                log_fp.flush()
            except Exception:
                pass

        # Cap history length (excluding system message)
        max_keep = max(0, int(args.max_messages))
        if len(messages) > 1 + max_keep:
            # keep system at index 0 and last `max_keep` messages
            tail = messages[-max_keep:] if max_keep > 0 else []
            messages = [messages[0]] + tail

    # Close log file on exit
    if log_fp is not None:
        try:
            log_fp.close()
            print(f"📝 Saved log: {log_path}")
        except Exception:
            pass

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