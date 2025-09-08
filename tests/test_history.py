import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from qwen_cli.core.cli import main


def run_cli_with_input(args, input_seq):
    it = iter(input_seq)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    buf = io.StringIO()
    code = 0
    import builtins as blt

    with redirect_stdout(buf):
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


def test_chat_logging_creates_jsonl(monkeypatch, tmp_path):
    # Dummy Ollama that streams a small reply
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
            # respond using last user message
            last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
            yield f"Echo: {last_user}"

    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", Dummy)

    history_dir = tmp_path / "history"
    code, _ = run_cli_with_input(
        [
            "chat",
            "--model",
            "qwen:latest",
            "--history-dir",
            str(history_dir),
            # logging is enabled by default now
        ],
        ["hello", "/exit"],
    )
    assert code == 0

    # Ensure a JSONL file was written
    files = list(history_dir.glob("session-*.jsonl"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8").strip().splitlines()
    # Expect at least system, user, assistant lines
    roles = [json.loads(line)["role"] for line in content]
    assert roles[0] == "system"
    assert "user" in roles
    assert "assistant" in roles


def test_chat_loads_prior_session(monkeypatch, tmp_path):
    captured_messages = {}

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
            captured_messages["messages"] = messages
            yield "ok"

    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", Dummy)

    # Create a prior session file
    history_dir = tmp_path / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    prior = history_dir / "prior.jsonl"
    lines = [
        json.dumps({"role": "system", "content": "You are Qwen"}),
        json.dumps({"role": "user", "content": "remember my name is Alice"}),
        json.dumps({"role": "assistant", "content": "Okay"}),
    ]
    prior.write_text("\n".join(lines) + "\n", encoding="utf-8")

    code, _ = run_cli_with_input(
        [
            "chat",
            "--model",
            "qwen:latest",
            "--history-dir",
            str(history_dir),
            "--session",
            str(prior),
        ],
        ["what is my name?", "/exit"],
    )
    assert code == 0
    # Verify that prior user/assistant turns were included
    msgs = captured_messages.get("messages", [])
    assert any(m.get("role") == "user" and "my name is Alice" in m.get("content", "") for m in msgs)
    assert any(m.get("role") == "assistant" for m in msgs)


