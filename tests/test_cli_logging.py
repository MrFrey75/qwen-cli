import io
from contextlib import redirect_stdout

from qwen_cli.core.cli import main


def run_cli(args, input_seq):
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


def test_chat_logs_to_default_dir(monkeypatch, tmp_path):
    # Redirect logs directory via env
    monkeypatch.setenv("QWEN_LOG_DIR", str(tmp_path / "logs"))

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
            yield "ok"

    monkeypatch.setenv("QWEN_OLLAMA_HOST", "http://localhost:11434")
    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", Dummy)

    # Also direct chat history into tmp_path via --history-dir
    history_dir = tmp_path / "hist"
    code, out = run_cli(["chat", "--model", "qwen:latest", "--history-dir", str(history_dir), "--title", "test" , "--no-log"], ["/exit"])
    assert code == 0

    # Logger should have created a rotating log file under QWEN_LOG_DIR
    logfile = (tmp_path / "logs" / "qwen-cli.log")
    assert logfile.exists()

