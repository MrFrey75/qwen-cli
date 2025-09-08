import io
from contextlib import redirect_stdout

import pytest

from qwen_cli.core.cli import main


def run_cli(args, input_seq):
    # input_seq: iterable of strings to feed into input()
    it = iter(input_seq)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    buf = io.StringIO()
    code = 0
    with redirect_stdout(buf):
        import builtins as blt

        orig_input = blt.input
        try:
            blt.input = fake_input
            try:
                code = main(args)
            except SystemExit as e:
                code = int(e.code) if isinstance(e.code, int) else 0
        finally:
            blt.input = orig_input
    return code, buf.getvalue()


def test_chat_start_and_exit(monkeypatch):
    # Stub OllamaInterface with happy path
    class Dummy:
        def __init__(self, host=None):
            pass

        def is_ollama_running(self):
            return True

        def list_models(self):
            return ["qwen:latest"]

        def pull_model(self, model):
            return True

        def chat(self, model, messages, stream=True):
            yield "Hello"

    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", Dummy)

    code, out = run_cli(["chat"], ["/exit"])
    assert code == 0
    assert "Interactive chat started" in out
    assert "Bye" in out


def test_chat_pull_and_reset_and_message(monkeypatch):
    calls = {"pull": 0}

    class Dummy:
        def __init__(self, host=None):
            pass

        def is_ollama_running(self):
            return True

        def list_models(self):
            return []  # Force pull

        def pull_model(self, model):
            calls["pull"] += 1
            return True

        def chat(self, model, messages, stream=True):
            # ensure that previous user message is present in history
            assert any(m.get("role") == "user" and m.get("content") == "hello" for m in messages)
            yield "Hi"

    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", Dummy)

    code, out = run_cli(["chat", "--model", "qwen:latest", "-y"], ["hello", "/reset", "/exit"])
    assert code == 0
    assert calls["pull"] == 1
    assert "Hi" in out
    assert "Context reset" in out


