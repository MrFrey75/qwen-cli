import os
from pathlib import Path

from qwen_cli.core.logger import get_logger


def test_get_logger_writes_to_custom_dir(monkeypatch, tmp_path):
    log_dir = tmp_path / "logs"
    monkeypatch.setenv("QWEN_LOG_DIR", str(log_dir))
    monkeypatch.setenv("QWEN_LOG_LEVEL", "DEBUG")
    logger = get_logger("qwen.test")
    logger.debug("hello world")

    # Ensure file created under custom dir
    logfile = log_dir / "qwen-cli.log"
    assert logfile.exists()
    content = logfile.read_text(encoding="utf-8")
    assert "hello world" in content


