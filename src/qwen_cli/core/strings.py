# src/qwen_cli/core/strings.py
DEFAULT_STRINGS = {
    "init_start": "Initializing Qwen CLI workspace...",
    "init_dir_create": "Created workspace directory: {path}",
    "init_config_saved": "Saved default config to: {path}",
    "init_strings_saved": "Saved UI strings to: {path}",
    "init_complete": "✅ Setup complete. You're ready to go!",
    "error_write_failed": "Failed to write {file}: {error}",
    "error_mkdir_failed": "Failed to create directory: {error}",
    "error_invalid_json": "Invalid JSON in {file}: {error}",
    "error_missing_api_key": "DASHSCOPE_API_KEY not found in environment.",
    "help_text": """
Usage: qwen-cli [OPTIONS] [PROMPT]

Options:
  --init              Initialize workspace
  --dir PATH          Custom workspace directory
  --help              Show this help message
""",
}