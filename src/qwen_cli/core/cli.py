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
from .config import QwenConfig


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


def cmd_config(args):
    cfg = QwenConfig.load()
    if args.config_cmd == "path":
        print(cfg.path)
        return
    if args.config_cmd == "get":
        val = getattr(cfg, args.key, None)
        if val is None:
            print("")
        else:
            print(val)
        return
    if args.config_cmd == "set":
        key = args.key
        value = args.value
        # Basic casting for known fields
        if key == "max_messages":
            try:
                value = int(value)
            except Exception:
                print("❌ max_messages must be an integer")
                sys.exit(2)
        setattr(cfg, key, value)
        saved = cfg.save()
        print(f"✅ Saved {key} to {saved}")
        return
    if args.config_cmd == "list":
        import json as _json
        print(_json.dumps(cfg.__dict__, indent=2))
        return
    # default: show help
    print("Use: qwen config [path|get|set|list]")


def cmd_test(args):
    """Run pytest -v and stream results to stdout."""
    import subprocess
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "-v"], check=False)
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return 1

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
    # New scheme: <title>-YYYY-MM-DD-[i].jsonl and roll to next i when file exceeds max bytes
    max_bytes = int(os.environ.get("QWEN_HISTORY_MAX_BYTES", str(1 * 1024 * 1024)))  # 1MB default
    safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in (args.title or "session")).strip("-") or "session"
    date_str = datetime.now().strftime("%Y-%m-%d")

    def _next_index(start_at: int = 1) -> int:
        # Determine next available index by scanning existing files
        existing = list(history_dir.glob(f"{safe_title}-{date_str}-*.jsonl"))
        max_i = 0
        for p in existing:
            try:
                stem = p.stem  # e.g., title-YYYY-MM-DD-2
                i_str = stem.split("-")[-1]
                i_val = int(i_str)
                if i_val > max_i:
                    max_i = i_val
            except Exception:
                continue
        return max(max_i, start_at)

    def _open_log(index: int):
        path = history_dir / f"{safe_title}-{date_str}-{index}.jsonl"
        fp = path.open("a", encoding="utf-8")
        return fp, path

    def _maybe_rotate():
        nonlocal log_fp, log_path
        if log_fp is None:
            return
        try:
            size = log_path.stat().st_size
            if size >= max_bytes:
                # roll to next index
                try:
                    current_i = int(log_path.stem.split("-")[-1])
                except Exception:
                    current_i = _next_index()
                log_fp.close()
                next_i = current_i + 1
                new_fp, new_path = _open_log(next_i)
                log_fp, log_path = new_fp, new_path
                print(f"📝 Rolled log to: {log_path}")
        except Exception:
            pass

    if not args.no_log:
        try:
            start_i = _next_index(1)
            log_fp, log_path = _open_log(start_i)
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
                _maybe_rotate()
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
                _maybe_rotate()
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
    if parsed.command == "config":
        cmd_config(parsed)
        return 0
    if parsed.command == "test":
        return cmd_test(parsed)

    # If no valid command, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())