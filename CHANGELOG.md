# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-09-08

### Added
- `qwen chat` interactive mode with in-memory history, system prompt, and `/reset`/`/exit` commands.
- CLI flags and env vars: `--model`/`QWEN_MODEL`, `--host`/`QWEN_OLLAMA_HOST`, `-y/--yes`.
- Ollama chat support via `/api/chat` with streaming.

### Changed
- Single-sourced version via `qwen_cli.__version__` and dynamic version in `pyproject.toml`.
- Hardened HTTP requests in Ollama interface with timeouts and status checks.
- Cleaned packaging metadata; removed duplicate version and deprecated script entry.

### Docs
- README: installation, usage, options, troubleshooting, and chat mode examples.


