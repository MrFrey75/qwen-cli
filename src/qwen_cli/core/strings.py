
# src/qwen_cli/core/strings.py
DEFAULT_STRINGS = {
    "app_title": "Qwen CLI – Local-first (Ollama)",
    "help_text": """
Usage: qwen-cli [OPTIONS] [PROMPT]

Options:
  --init                 Initialize workspace
  --dir PATH             Custom workspace directory
  --model NAME           Override model (default from config)
  --no-stream            Disable streaming
  --help                 Show this help message
Examples:
  qwen-cli --init
  qwen-cli "Write a haiku about compilers"
  qwen-cli --model qwen2.5:1.5b-instruct "Summarize RFC 2616"
""".strip(),
    "init_started": "Initializing workspace...",
    "init_done": "✅ Setup complete. You're ready to go!",
    "init_dir": "Workspace: {path}",
    "saved_file": "Saved {what} to: {path}",
    "interactive_banner": "Entering interactive mode. Type /exit to quit, /config to view config.",
    "missing_workspace": "Workspace not initialized. Run: qwen-cli --init",
    "err_write": "Failed to write {file}: {error}",
}