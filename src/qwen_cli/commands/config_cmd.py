import sys
import json as _json
from qwen_cli.core.config import QwenConfig


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
        print(_json.dumps(cfg.__dict__, indent=2))
        return
    print("Use: qwen config [path|get|set|list]")


