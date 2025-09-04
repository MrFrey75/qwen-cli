
# src/qwen_cli/core/workspace.py
from __future__ import annotations
import json
import os
from pathlib import Path
from .strings import DEFAULT_STRINGS
from .config import Config, load_config, save_config

DEFAULT_FILES = {
    "strings.json": DEFAULT_STRINGS,
    "system_prompt.txt": "You are Qwen CLI running locally via Ollama. Be concise and helpful."
}

def get_workspace_path(custom: str | None = None) -> Path:
    if custom:
        return Path(custom).expanduser().resolve()
    return Path(os.getenv("QWEN_CLI_HOME", "~/.qwen-cli")).expanduser()

def is_setup_complete(workspace: Path) -> bool:
    return (workspace / "config.json").exists()

def run_initialization(workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    # write defaults if not present
    if not (workspace / "config.json").exists():
        save_config(workspace, Config())
    for name, data in DEFAULT_FILES.items():
        p = workspace / name
        if not p.exists():
            if isinstance(data, dict):
                p.write_text(json.dumps(data, indent=2), encoding="utf-8")
            else:
                p.write_text(str(data), encoding="utf-8")