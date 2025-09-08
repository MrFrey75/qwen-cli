# 🤖 Qwen CLI – Your Local AI Assistant

> A secure, extensible, personal AI assistant that runs entirely **on your machine**.  
> No data leaves your device. No cloud. No tracking.

Qwen CLI is a command-line interface powered by **Qwen** via **Ollama**, designed to evolve from a simple CLI into a context-aware, multimodal companion — one safe, verifiable step at a time.

Built with:
- 🔐 **Local-first** – All processing happens on-device
- 🧩 **Extensible** – Plugin-ready for AI-generated tools
- 🚦 **Opt-in** – Nothing activates without your consent
- 📦 **Self-contained** – Works offline with Ollama

---

## 🚀 Quick Start

### 1. Requirements

- Install [Ollama](https://ollama.com/download)
- Python 3.10+

### 2. Install

Dev install:

```bash
pip install -e .
```

Or run via pipx:

```bash
pipx install .
```

### 3. Pull a model (one-time)

You can let the CLI pull it for you, or do it manually:

```bash
ollama run qwen:latest
```

### 4. Use

```bash
qwen --help
qwen --version
qwen ask "What is Python?"
qwen chat
```

Options:

- `--model` (or `QWEN_MODEL`): choose model, default `qwen:latest`
- `--host` (or `QWEN_OLLAMA_HOST`): Ollama host, default `http://localhost:11434`
- `-y/--yes`: auto-confirm model downloads

Interactive chat tips:

- Start chat: `qwen chat`
- Reset context: type `/reset`
- Exit: type `/exit`, `:q`, or press Ctrl+D

## Development Roadmap

[Roadmap](docs/roadmap.md)

---

## Troubleshooting

- Ollama not running: ensure `ollama serve` is active and `http://localhost:11434` reachable.
- Model missing: use `qwen -y ask "..."` to auto-pull or run `ollama run qwen:latest`.
- Connection issues: check firewall/VPN; set `--host` if Ollama runs on another address.