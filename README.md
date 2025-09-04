# qwen-cli

## Documentation

- [README](./README.md)
- [CHANGELOG](./CHANGELOG.md)
- [LICENSE](./LICENSE)
- [Project Docs](./docs/README.md)
  - [Project Roadmap](./docs/roadmap.md)

## Source

- [qwen-cli repo](https://github.com/MrFrey75/qwen-cli.git)

## Local Qwen via Ollama

This fork is wired to **Ollama** instead of DashScope.

### Prereqs
- Install [Ollama](https://ollama.com) and pull a small Qwen model:
  ```bash
  ollama pull qwen2.5:1.5b-instruct
  ```
- (Optional) set a different base URL:
  ```bash
  export OLLAMA_BASE_URL=http://localhost:11434
  ```

### Usage
```bash
pip install -e .
qwen-cli --init
qwen-cli "Explain tail recursion"
qwen-cli --model qwen2.5:1.5b-instruct "Write a pytest for fizzbuzz"
```