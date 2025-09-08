import builtins
import io
import sys
from contextlib import redirect_stdout

import pytest

from qwen_cli.core.cli import main


def run_cli(args):
    buf = io.StringIO()
    code = 0
    with redirect_stdout(buf):
        try:
            code = main(args)
        except SystemExit as e:
            code = int(e.code) if isinstance(e.code, int) else 0
    return code, buf.getvalue()


def test_cli_help_shows_when_no_args():
    code, out = run_cli([])
    assert code == 0
    assert "Available commands" in out


def test_cli_version_flag():
    # argparse handles printing version and exiting
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0


def test_cli_ask_requires_ollama(monkeypatch):
    class Dummy:
        def is_ollama_running(self):
            return False

    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", lambda host=None: Dummy())
    code, out = run_cli(["ask", "hi"]) 
    # When ollama not running, cmd exits with code 1
    assert "Ollama is not running" in out


