def test_version_present():
    import qwen_cli

    assert hasattr(qwen_cli, "__version__")
    assert isinstance(qwen_cli.__version__, str)
    assert len(qwen_cli.__version__) > 0


