from pathlib import Path

from qwen_cli.core.config import QwenConfig


def test_config_loads_defaults_and_saves(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "configs"
    cfg_file = cfg_dir / "config.json"
    monkeypatch.setenv("QWEN_CONFIG", str(cfg_file))

    # Load when missing → defaults
    cfg = QwenConfig.load()
    assert cfg.model == "qwen:latest"
    assert cfg.host.startswith("http://")
    assert cfg.max_messages == 20

    # Save and verify file exists
    saved_path = cfg.save()
    assert saved_path == cfg_file
    assert cfg_file.exists()

    # Change a value and persist
    cfg.model = "qwen:custom"
    cfg.max_messages = 42
    cfg.save()

    # Reload and verify values applied
    cfg2 = QwenConfig.load()
    assert cfg2.model == "qwen:custom"
    assert cfg2.max_messages == 42


def test_cli_uses_config_defaults(tmp_path, monkeypatch):
    # Point config path and write custom defaults
    cfg_dir = tmp_path / "configs"
    cfg_file = cfg_dir / "config.json"
    monkeypatch.setenv("QWEN_CONFIG", str(cfg_file))

    cfg = QwenConfig()
    cfg.model = "qwen:test"
    cfg.host = "http://localhost:11434"
    cfg.max_messages = 7
    cfg.history_dir = str(tmp_path / "logs")
    cfg.title = "t"
    cfg.save()

    # Run chat and ensure it starts without specifying flags, picking up config
    from qwen_cli.core.cli import main
    import io
    from contextlib import redirect_stdout
    import builtins as blt

    def run(args, inputs):
        it = iter(inputs)

        def fake_input(prompt=""):
            try:
                return next(it)
            except StopIteration:
                raise EOFError

        buf = io.StringIO()
        with redirect_stdout(buf):
            orig = blt.input
            try:
                blt.input = fake_input
                try:
                    code = main(args)
                except SystemExit as e:
                    code = int(e.code) if isinstance(e.code, int) else 0
            finally:
                blt.input = orig
        return code, buf.getvalue()

    class Dummy:
        def __init__(self, host=None):
            assert host == cfg.host

        def is_ollama_running(self):
            return True

        def list_models(self):
            return [cfg.model]

        def pull_model(self, model):
            return True

        def chat(self, model, messages, stream=True):
            # Ensure model and history cap are from config
            assert model == cfg.model
            # 1 system + user + assistant fits under cap
            yield "ok"

    monkeypatch.setenv("QWEN_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr("qwen_cli.core.cli.OllamaInterface", Dummy)

    code, out = run(["chat"], ["hello", "/exit"])
    assert code == 0
    assert "Interactive chat started" in out


