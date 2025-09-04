# src/qwen_cli/core/ollama.py
"""
Interface to local Ollama API.
Handles model availability, pulling, and generation.
"""

import requests
import sys
from typing import Generator, Optional


class OllamaInterface:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host

    def is_ollama_running(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            requests.get(f"{self.host}/api/tags", timeout=5)
            return True
        except requests.RequestException:
            return False

    def list_models(self) -> list:
        """Get list of available models."""
        try:
            resp = requests.get(f"{self.host}/api/tags")
            if resp.status_code == 200:
                return [m["name"] for m in resp.json().get("models", [])]
            return []
        except Exception:
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
            )
            for line in resp.iter_lines():
                if line:
                    try:
                        data = line.decode("utf-8")
                        print(f" → {data}")
                    except Exception:
                        print(" → ...")
            return True
        except KeyboardInterrupt:
            print("\n❌ Model pull cancelled by user.")
            return False
        except Exception as e:
            print(f"\n❌ Failed to pull model: {e}")
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
            )
            for line in resp.iter_lines():
                if line:
                    try:
                        data = line.decode("utf-8")
                        import json
                        obj = json.loads(data)
                        if "response" in obj:
                            yield obj["response"]
                    except Exception:
                        yield ""
        except Exception as e:
            yield f"\n❌ Error: {e}"