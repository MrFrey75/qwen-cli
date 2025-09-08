import json

import pytest

from qwen_cli.core.ollama import OllamaInterface


class DummyResponse:
    def __init__(self, status_code=200, lines=None):
        self.status_code = status_code
        self._lines = lines or []

    def iter_lines(self):
        for l in self._lines:
            yield l


def test_is_ollama_running_true(monkeypatch):
    def fake_get(url, timeout=None):
        return DummyResponse(200)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)
    o = OllamaInterface()
    assert o.is_ollama_running() is True


def test_list_models_returns_names(monkeypatch):
    def fake_get(url, timeout=None):
        payload = {"models": [{"name": "qwen:latest"}]}
        resp = DummyResponse(200)
        resp.json = lambda: payload
        return resp

    import requests

    monkeypatch.setattr(requests, "get", fake_get)
    o = OllamaInterface()
    assert "qwen:latest" in o.list_models()


def test_generate_streams_content(monkeypatch):
    def fake_post(url, json=None, stream=False, timeout=None):
        lines = [
            jsonlib.dumps({"response": "Hello"}).encode("utf-8"),
            jsonlib.dumps({"response": " world"}).encode("utf-8"),
        ]
        return DummyResponse(200, lines=lines)

    import requests as requests_module
    import json as jsonlib

    monkeypatch.setattr(requests_module, "post", fake_post)
    o = OllamaInterface()
    chunks = list(o.generate("qwen:latest", "hi"))
    assert "".join(chunks).strip().startswith("Hello")


def test_chat_streams_content(monkeypatch):
    def fake_post(url, json=None, stream=False, timeout=None):
        lines = [
            jsonlib.dumps({"message": {"content": "Hi"}}).encode("utf-8"),
            jsonlib.dumps({"message": {"content": ", there"}}).encode("utf-8"),
        ]
        return DummyResponse(200, lines=lines)

    import requests as requests_module
    import json as jsonlib

    monkeypatch.setattr(requests_module, "post", fake_post)
    o = OllamaInterface()
    chunks = list(o.chat("qwen:latest", messages=[{"role": "user", "content": "hi"}]))
    assert "".join(chunks).startswith("Hi")


