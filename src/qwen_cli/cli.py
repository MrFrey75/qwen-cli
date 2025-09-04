
# src/qwen_cli/cli.py
from __future__ import annotations
import argparse
import sys
from .core.workspace import run_initialization, get_workspace_path, is_setup_complete
from .core.config import load_config, save_config, Config
from .core.strings import DEFAULT_STRINGS
from .core.ollama_client import chat

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    p = argparse.ArgumentParser(description="Qwen CLI – Local (Ollama)", add_help=False)
    p.add_argument("prompt", nargs="?", help="One-shot prompt text")
    p.add_argument("--init", action="store_true", help="Initialize workspace")
    p.add_argument("--dir", type=str, help="Custom workspace directory")
    p.add_argument("--model", type=str, help="Override model name")
    p.add_argument("--no-stream", action="store_true", help="Disable streaming output")
    p.add_argument("--help", action="store_true", help="Show help text")
    args = p.parse_args(argv)

    if args.help:
        print(DEFAULT_STRINGS["help_text"])
        return 0

    ws = get_workspace_path(args.dir)

    if args.init:
        print(DEFAULT_STRINGS["init_started"])
        run_initialization(ws)
        print(DEFAULT_STRINGS["init_dir"].format(path=ws))
        print(DEFAULT_STRINGS["init_done"])
        return 0

    if not is_setup_complete(ws):
        print(DEFAULT_STRINGS["missing_workspace"])
        return 1

    cfg = load_config(ws)
    if args.model:
        cfg.model = args.model
        save_config(ws, cfg)

    stream = not args.no_stream

    if args.prompt:
        # one-shot
        messages = [{"role": "user", "content": args.prompt}]
        if stream:
            for chunk in chat(cfg.base_url, cfg.model, messages, stream=True, temperature=cfg.temperature, top_p=cfg.top_p, max_tokens=cfg.max_tokens):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print()
        else:
            res = chat(cfg.base_url, cfg.model, messages, stream=False, temperature=cfg.temperature, top_p=cfg.top_p, max_tokens=cfg.max_tokens)
            print(res.get("message", {}).get("content", ""))
        return 0

    # Interactive loop
    print(DEFAULT_STRINGS["interactive_banner"])
    history = []
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not user:
            continue
        if user in {"/exit", ":q"}:
            return 0
        if user == "/config":
            print(cfg)
            continue
        history.append({"role": "user", "content": user})
        if stream:
            for chunk in chat(cfg.base_url, cfg.model, history, stream=True, temperature=cfg.temperature, top_p=cfg.top_p, max_tokens=cfg.max_tokens):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print()
        else:
            res = chat(cfg.base_url, cfg.model, history, stream=False, temperature=cfg.temperature, top_p=cfg.top_p, max_tokens=cfg.max_tokens)
            ai = res.get("message", {}).get("content", "")
            print(ai)
            history.append({"role": "assistant", "content": ai})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())