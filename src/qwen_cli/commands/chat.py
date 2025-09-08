import json
import os
import sys
from datetime import datetime
from pathlib import Path

from qwen_cli.core.logger import get_logger
from qwen_cli.core.ollama import OllamaInterface


def cmd_chat(args):
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
        existing = list(history_dir.glob(f"{safe_title}-{date_str}-*.jsonl"))
        max_i = 0
        for p in existing:
            try:
                stem = p.stem
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
            augmented = [messages[0]]
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

        messages.append({"role": "assistant", "content": assistant_content})
        if log_fp is not None:
            try:
                _maybe_rotate()
                log_fp.write(json.dumps({"role": "assistant", "content": assistant_content}) + "\n")
                log_fp.flush()
            except Exception:
                pass

        max_keep = max(0, int(args.max_messages))
        if len(messages) > 1 + max_keep:
            tail = messages[-max_keep:] if max_keep > 0 else []
            messages = [messages[0]] + tail


