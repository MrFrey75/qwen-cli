# tests/test_phase0.py
import os
import tempfile
import shutil
import json
from pathlib import Path
from qwen_cli.core.workspace import (
    get_workspace_path,
    ensure_workspace_dir,
    is_setup_complete,
    run_initialization,
    DEFAULT_CONFIG,
    DEFAULT_STRINGS,
    CONFIG_FILE,
    STRINGS_FILE,
    FLAG_FILE
)

def test_get_workspace_path():
    default = get_workspace_path()
    assert default == Path.home() / ".qwen-cli"

    custom = get_workspace_path("/tmp/test-qwen")
    assert custom == Path("/tmp/test-qwen").resolve()

def test_ensure_workspace_dir():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "qwen-test"
        result = ensure_workspace_dir(path)
        assert result is True
        assert path.exists() and path.is_dir()

def test_run_initialization():
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "qwen-cli"
        success = run_initialization(str(workspace))
        assert success is True

        # Check files
        assert (workspace / CONFIG_FILE).exists()
        assert (workspace / STRINGS_FILE).exists()
        assert (workspace / FLAG_FILE).exists()

        # Check config.json content
        with open(workspace / CONFIG_FILE) as f:
            config = json.load(f)
        assert config == DEFAULT_CONFIG

        # Check strings.json
        with open(workspace / STRINGS_FILE) as f:
            strings = json.load(f)
        assert strings == DEFAULT_STRINGS

def test_is_setup_complete():
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "qwen-cli"
        (workspace / FLAG_FILE).parent.mkdir()
        (workspace / FLAG_FILE).touch()
        assert is_setup_complete(workspace) is True

        workspace2 = Path(tmp) / "empty"
        assert is_setup_complete(workspace2) is False