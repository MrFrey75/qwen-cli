import json
import os
import sys
from datetime import datetime
from pathlib import Path
import spacy

from qwen_cli.core.logger import get_logger
from qwen_cli.core.ollama import OllamaInterface

# NOTE: This assumes you have a new file `chat_logger.py` with the ChatLogger class.
from qwen_cli.core.chat_logger import ChatLogger


# Lazy load spaCy model for Named Entity Recognition (NER)
# The 'en_core_web_sm' model can identify entities like 'PERSON' and 'GPE' (geopolitical entity).
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("❌ spaCy model 'en_core_web_sm' not found. Please install it with:")
    print("python -m spacy download en_core_web_sm")
    sys.exit(1)


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

    # Prepare logging
    chat_logger = None
    if not args.no_log:
        try:
            history_dir = Path(args.history_dir)
            history_dir.mkdir(parents=True, exist_ok=True)
            chat_logger = ChatLogger(history_dir, args.title)
            chat_logger.log_message("system", args.system)
        except Exception as e:
            print(f"⚠️  Could not open log file: {e}")
            chat_logger = None

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

        # Use spaCy for more robust fact extraction.
        doc = nlp(user_input)
        for ent in doc.ents:
            # spaCy's NER can identify various entities like PERSON, GPE (countries, cities, states), and LOC (non-GPE locations).
            if ent.label_ == "PERSON":
                session_facts["name"] = ent.text
            elif ent.label_ in ("GPE", "LOC"):
                session_facts["location"] = ent.text

        messages.append({"role": "user", "content": user_input})
        if chat_logger:
            chat_logger.log_message("user", user_input)

        print("🤖 Qwen: ", end="", flush=True)
        try:
            assistant_content = ""
            augmented = [messages[0]]
            if session_facts:
                facts_lines = []
                if "name" in session_facts:
                    facts_lines.append(f"User name: {session_facts['name']}")
                if "location" in session_facts:
                    facts_lines.append(f"User location: {session_facts['location']}")
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
        if chat_logger:
            chat_logger.log_message("assistant", assistant_content)

        max_keep = max(0, int(args.max_messages))
        if len(messages) > 1 + max_keep:
            tail = messages[-max_keep:] if max_keep > 0 else []
            messages = [messages[0]] + tail