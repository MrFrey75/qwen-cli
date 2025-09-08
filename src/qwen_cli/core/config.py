"""
Configuration management for Qwen CLI.

Stores and loads user settings from a JSON file.
Default location: ~/.qwen/config.json (overridable by QWEN_CONFIG)

Schema (keys are optional; defaults applied when missing):
- assistant-name: str (default "Qwen")
- user-name: str (default "User")
- model: str (default "qwen:latest")
- host: str (default "http://localhost:11434")
- history_dir: str (default ./logs)
- max_messages: int (default 20)
- system_prompt: str
- title: str (default "session")
- logging-level: str (default "info")
- response-format: str (default "markdown")
- session_timeout_minutes: int (default 30)
- temperature: float (default 0.7)
- persona.role: str (default "assistant")
- persona.style: str (default "conversational")
- persona.verbosity: str (default "concise")
- persona.formality: str (default "neutral")

"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict


def _default_config_path() -> Path:
    env = os.environ.get("QWEN_CONFIG")
    if env:
        return Path(env).expanduser()
    # Default to project-local config directory
    return Path.cwd() / "config" / "config.json"


def _default_logs_dir() -> str:
    return str(Path.cwd() / "logs")


DEFAULT_SYSTEM = (
    "You are Qwen, a helpful assistant. Always use the conversation history to answer. "
    "If the user has provided personal details (like name) earlier in this session, "
    "use them when helpful. Keep answers concise."
)


@dataclass
class QwenConfig:
    model: str = "qwen:latest"
    host: str = "http://localhost:11434"
    history_dir: str = _default_logs_dir()
    max_messages: int = 20
    system_prompt: str = DEFAULT_SYSTEM
    title: str = "session"

    @classmethod
    def load(cls, path: Path | None = None) -> "QwenConfig":
        cfg_path = path or _default_config_path()
        try:
            if cfg_path.exists():
                data = json.loads(cfg_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("config root must be a JSON object")
                return cls(**{**asdict(cls()), **data})  # type: ignore[arg-type]
            else:
                # First run: create default config file on disk
                default_cfg = cls()
                cfg_path.parent.mkdir(parents=True, exist_ok=True)
                with cfg_path.open("w", encoding="utf-8") as f:
                    json.dump(asdict(default_cfg), f, indent=2, ensure_ascii=False)
                return default_cfg
        except Exception:
            # On any error, fall back to defaults
            pass
        return cls()

    def save(self, path: Path | None = None) -> Path:
        cfg_path = path or _default_config_path()
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        return cfg_path

    @property
    def path(self) -> Path:
        return _default_config_path()


