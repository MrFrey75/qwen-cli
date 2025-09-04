
# src/qwen_cli/core/ollama_client.py
from __future__ import annotations
import json
import requests
from typing import Iterable, List, Dict, Any, Generator

def chat(base_url: str, model: str, messages: List[Dict[str, str]], stream: bool = True, **params) -> Iterable[str] | Dict[str, Any]:
    """Call Ollama's /api/chat.
    If stream=True, yields content chunks (strings). Otherwise returns the final response dict.
    """
    url = base_url.rstrip('/') + '/api/chat'
    payload = {
        "model": model,
        "messages": messages,
        "stream": bool(stream),
    }
    # Map selected params
    for k in ("temperature", "top_p", "max_tokens"):
        if k in params and params[k] is not None:
            payload[k] = params[k]
    if stream:
        with requests.post(url, json=payload, stream=True, timeout=300) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    obj = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                delta = obj.get("message", {}).get("content", "")
                if delta:
                    yield delta
    else:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()