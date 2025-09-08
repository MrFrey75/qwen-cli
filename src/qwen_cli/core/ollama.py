"""
Interface to local Ollama API.
Handles model availability, pulling, and generation.

file: src/qwen_cli/core/ollama.py
"""

import requests
import sys
from typing import Generator, Optional, List, Dict, Any
from .logger import get_logger


class OllamaInterface:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self._log = get_logger("qwen.ollama")

    def is_ollama_running(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            ok = resp.status_code == 200
            if not ok:
                self._log.warning("Ollama healthcheck failed: HTTP %s", resp.status_code)
            return ok
        except requests.RequestException:
            self._log.exception("Failed to reach Ollama at %s", self.host)
            return False

    def list_models(self) -> list:
        """Get list of available models."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = [m.get("name", "") for m in resp.json().get("models", []) if isinstance(m, dict)]
                self._log.debug("Available models: %s", models)
                return models
            return []
        except requests.RequestException:
            self._log.exception("Error listing models from Ollama")
            return []

    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama with streaming output."""
        print(f"📥 Pulling model '{model}'... (this may take a while)")
        print("Press Ctrl+C to cancel.")

        try:
            resp = requests.post(
                f"{self.host}/api/pull",
                json={"name": model},
                stream=True,
                timeout=60,
            )
            if resp.status_code != 200:
                print(f"❌ Failed to start model pull (HTTP {resp.status_code}).")
                self._log.error("Pull start failed for %s: HTTP %s", model, resp.status_code)
                return False

            for line in resp.iter_lines():
                if line:
                    try:
                        data = line.decode("utf-8")
                        print(f" → {data}")
                        self._log.debug("pull %s: %s", model, data)
                    except Exception:
                        print(" → ...")
            return True
        except KeyboardInterrupt:
            print("\n❌ Model pull cancelled by user.")
            self._log.info("Model pull cancelled by user for %s", model)
            return False
        except requests.RequestException as e:
            print(f"\n❌ Failed to pull model: {e}")
            self._log.exception("Model pull failed for %s", model)
            return False

    def generate(self, model: str, prompt: str, stream: bool = True) -> Generator[str, None, None]:
        """Generate response from model."""
        try:
            resp = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": stream,
                },
                stream=stream,
                timeout=60,
            )
            if resp.status_code != 200:
                yield f"\n❌ Generation failed (HTTP {resp.status_code})."
                self._log.error("Generate failed for %s: HTTP %s", model, resp.status_code)
                return

            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = line.decode("utf-8")
                    import json
                    obj = json.loads(data)
                    if "response" in obj:
                        yield obj["response"]
                except Exception as e:
                    yield f"\n"
        except requests.RequestException as e:
            yield f"\n❌ Error: {e}"
            self._log.exception("Generate request failed for %s", model)

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        stream: bool = True,
    ) -> Generator[str, None, None]:
        """Chat with the model using /api/chat with message history.

        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        """
        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": stream,
                },
                stream=stream,
                timeout=60,
            )
            if resp.status_code != 200:
                yield f"\n❌ Chat failed (HTTP {resp.status_code})."
                self._log.error("Chat failed for %s: HTTP %s", model, resp.status_code)
                return

            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = line.decode("utf-8")
                    import json
                    obj = json.loads(data)
                    # Ollama chat stream emits chunks containing 'message': {'content': ...}
                    message = obj.get("message") or {}
                    content = message.get("content")
                    if content:
                        yield content
                except Exception:
                    yield "\n"
        except requests.RequestException as e:
            yield f"\n❌ Error: {e}"
            self._log.exception("Chat request failed for %s", model)