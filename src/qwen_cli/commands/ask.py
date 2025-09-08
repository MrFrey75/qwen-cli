import sys
from qwen_cli.core.ollama import OllamaInterface
from qwen_cli.core.logger import get_logger


def cmd_ask(args):
    """Handle `qwen ask "prompt"` command."""
    log = get_logger("qwen.cli")
    ollama = OllamaInterface(host=args.host)

    if not ollama.is_ollama_running():
        print("❌ Ollama is not running.")
        log.error("Ollama not running at %s", args.host)
        print("Please start Ollama: https://ollama.com")
        sys.exit(1)

    model = args.model
    if model not in ollama.list_models():
        print(f"❌ Model '{model}' not found.")
        log.info("Model not found: %s", model)
        if not args.yes:
            confirm = input(f"👉 Would you like to pull '{model}'? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cannot proceed without model.")
                sys.exit(1)
        else:
            print("--yes provided; proceeding to pull model.")
            log.info("Auto-pulling model %s", model)
        if not ollama.pull_model(model):
            print("❌ Cannot proceed without model.")
            log.error("Model pull failed: %s", model)
            sys.exit(1)

    print(f"\n🤖 Qwen: ", end="", flush=True)
    try:
        for chunk in ollama.generate(model, args.prompt):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
        log.exception("Generation error for model %s", model)
        sys.exit(1)
    finally:
        print()  # Newline at end


