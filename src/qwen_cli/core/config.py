"""
Configuration management for Qwen CLI.

The config.json file is the single source of truth and is required to run the application.
This module will fail with an error if the config file is not found, is corrupt,
or is missing required keys.

Default location: ./config/config.json (overridable by QWEN_CONFIG)
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

def _default_config_path() -> Path:
    """Determines the path for the configuration file."""
    env = os.environ.get("QWEN_CONFIG")
    if env:
        return Path(env).expanduser()
    return Path.cwd() / "config" / "config.json"


@dataclass
class PersonaConfig:
    """Defines the persona of the assistant. Values are loaded from config.json."""
    role: str
    tone: str
    style: str
    verbosity: str
    personality_traits: List[str]
    formality: str
    humor: str = "none"  # Optional, defaults to "none" if missing
    additional_instructions: str = ""  # Optional, defaults to empty if missing


@dataclass
class QwenConfig:
    """Main configuration class. All values are loaded directly from config.json."""
    assistant_name: str
    user_name: str
    model: str
    host: str
    history_dir: str
    max_messages: int
    system_prompt: str
    title: str
    logging_level: str
    response_format: str
    session_timeout_minutes: int
    temperature: float
    persona: PersonaConfig


    @classmethod
    def load(cls, path: Path | None = None) -> "QwenConfig":
        """Loads configuration from JSON file. Exits if the file does not exist."""
        cfg_path = path or _default_config_path()

        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            persona_data = data.pop("persona")
            persona_obj = PersonaConfig(**persona_data)
            # Line 68 was here and has been removed.
            return cls(persona=persona_obj, **data)
        except FileNotFoundError:
            print(f"❌ Error: Configuration file not found at '{cfg_path}'.", file=sys.stderr)
            print("   This file is required to run the application. Please create one.", file=sys.stderr)
            sys.exit(1)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"❌ Error: Configuration file at '{cfg_path}' is corrupted or missing required keys.", file=sys.stderr)
            print(f"   Please ensure the file is valid. Details: {e}", file=sys.stderr)
            sys.exit(1)

    def save(self, path: Path | None = None) -> Path:
        """Saves the current configuration to a JSON file."""
        cfg_path = path or _default_config_path()
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        return cfg_path

    def build_system_prompt(self) -> str:
        """Constructs the full system prompt including persona details."""
        persona_details = (
            f"You are {self.assistant_name}, a {self.persona.tone} {self.persona.role}.\n"
            f"Your user's name is {self.user_name}.\n"
            f"Style: {self.persona.style}\n"
            f"Verbosity: {self.persona.verbosity}\n"
            f"Personality Traits: {', '.join(self.persona.personality_traits)}\n"
            f"Formality: {self.persona.formality}\n"
            f"Humor: {self.persona.humor}\n"
            f"Additional Instructions: {self.persona.additional_instructions}"
        )
        return f"{self.system_prompt}\n\n--- Persona Details ---\n{persona_details}"


    @property
    def path(self) -> Path:
        """Returns the path to the configuration file."""
        return _default_config_path()