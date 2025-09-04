# src/qwen_cli/core/workspace.py
import os
import json
from pathlib import Path

from .strings import DEFAULT_STRINGS

# Define default config here to avoid circular import
DEFAULT_CONFIG = {
    "model": "qwen-max",
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 2048,
    "stream": True
}

DEFAULT_WORKSPACE = Path.home() / ".qwen-cli"
CONFIG_FILE = "config.json"
STRINGS_FILE = "strings.json"
FLAG_FILE = ".setup_complete"


def get_workspace_path(custom_path: str = None) -> Path:
    """
    Determine the workspace path.
    Uses custom path if provided, otherwise defaults to ~/.qwen-cli.
    """
    if custom_path:
        return Path(custom_path).expanduser().resolve()
    return DEFAULT_WORKSPACE


def ensure_workspace_dir(workspace: Path) -> bool:
    """
    Create the workspace directory if it doesn't exist.
    Returns True on success, False on failure.
    """
    try:
        workspace.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"[ERROR] {DEFAULT_STRINGS['error_mkdir_failed'].format(error=e)}")
        return False


def is_setup_complete(workspace: Path) -> bool:
    """
    Check if initialization has already been completed.
    Looks for the presence of the .setup_complete flag file.
    """
    return (workspace / FLAG_FILE).exists()


def write_json_safely(path: Path, data: dict, message_key: str) -> bool:
    """
    Safely write a dictionary to a JSON file.
    Prints success or error message using externalized strings.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(DEFAULT_STRINGS[message_key].format(path=path))
        return True
    except Exception as e:
        print(f"[ERROR] {DEFAULT_STRINGS['error_write_failed'].format(file=path.name, error=e)}")
        return False


def run_initialization(custom_path: str = None) -> bool:
    """
    Run full workspace initialization:
    - Create directory
    - Save config.json
    - Save strings.json
    - Create .setup_complete flag

    Returns True if all steps succeed.
    """
    workspace = get_workspace_path(custom_path)

    print(DEFAULT_STRINGS["init_start"])

    if not ensure_workspace_dir(workspace):
        return False

    # Write config.json
    config_path = workspace / CONFIG_FILE
    if not write_json_safely(config_path, DEFAULT_CONFIG, "init_config_saved"):
        return False

    # Write strings.json
    strings_path = workspace / STRINGS_FILE
    if not write_json_safely(strings_path, DEFAULT_STRINGS, "init_strings_saved"):
        return False

    # Create setup flag
    flag_path = workspace / FLAG_FILE
    if not write_json_safely(flag_path, {}, "init_complete"):
        return False

    return True
