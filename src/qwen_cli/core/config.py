
# src/qwen_cli/core/config.py
from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict

DEFAULT_MODEL = os.getenv("QWEN_CLI_MODEL", "qwen2.5:1.5b-instruct")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

@dataclass
class Config:
    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stream: bool = True
    base_url: str = DEFAULT_BASE_URL

def load_config(workspace: Path) -> Config:
    cfg_path = workspace / "config.json"
    if not cfg_path.exists():
        return Config()
    try:
        data: Dict[str, Any] = json.loads(cfg_path.read_text(encoding="utf-8"))
        return Config(**{**asdict(Config()), **data})
    except Exception:
        return Config()

def save_config(workspace: Path, cfg: Config) -> None:
    cfg_path = workspace / "config.json"
    cfg_path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")