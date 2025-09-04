# src/qwen_cli/core/config.py
import json
from pathlib import Path
from typing import Dict, Any

def load_config(workspace: Path) -> Dict[str, Any]:
    """Load config.json; return defaults if not found or invalid"""
    config_path = workspace / "config.json"
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Merge with defaults
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except json.JSONDecodeError as e:
        print(f"[WARNING] Invalid config.json: {e}. Using defaults.")
    except Exception as e:
        print(f"[WARNING] Could not read config.json: {e}. Using defaults.")
    return DEFAULT_CONFIG.copy()

# Default config values
DEFAULT_CONFIG = {
    "model": "qwen-max",
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 2048,
    "stream": True
}