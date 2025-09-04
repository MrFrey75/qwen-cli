# src/qwen_cli/cli.py
import argparse
import os
from .core.workspace import run_initialization, get_workspace_path, is_setup_complete
from .core.strings import DEFAULT_STRINGS


def main():
    parser = argparse.ArgumentParser(
        description="Qwen CLI – A secure, local-first AI assistant",
        add_help=False  # We'll handle --help manually
    )
    parser.add_argument("prompt", nargs="?", help="One-shot prompt")
    parser.add_argument("--init", action="store_true", help="Initialize workspace")
    parser.add_argument("--dir", type=str, help="Custom workspace directory")
    parser.add_argument("--help", action="store_true", help="Show help message")

    args = parser.parse_args()

    if args.help:
        print(DEFAULT_STRINGS["help_text"])
        return

    if args.init:
        success = run_initialization(custom_path=args.dir)
        if not success:
            exit(1)
        return

    # Determine workspace
    workspace = get_workspace_path(args.dir)

    # Ensure setup has been completed
    if not is_setup_complete(workspace):
        print("Workspace not initialized. Run `qwen-cli --init` first.")
        exit(1)

    # Validate environment
    if not os.getenv("DASHSCOPE_API_KEY"):
        print(f"[ERROR] {DEFAULT_STRINGS['error_missing_api_key']}")
        exit(1)

    # Dispatch mode
    if args.prompt:
        print(f"[DEBUG] One-shot mode: {args.prompt}")
        # Future: Call API with prompt
    else:
        print("[DEBUG] Interactive mode not yet implemented")
        # Future: Enter chat loop


if __name__ == "__main__":
    main()