"""
Centralized logging utilities for Qwen CLI.

Provides a configured logger with rotating file handler and optional console output.
Configuration via environment variables:
- QWEN_LOG_DIR: directory for log files (default: ./logs)
- QWEN_LOG_LEVEL: logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO
- QWEN_LOG_TO_CONSOLE: '1' to enable console logging (default: '1')
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


_LOGGER_CACHE = {}


def _ensure_log_dir() -> Path:
    default_dir = Path.cwd() / "logs"
    log_dir = Path(os.environ.get("QWEN_LOG_DIR", str(default_dir)))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _resolve_level() -> int:
    level_name = os.environ.get("QWEN_LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def get_logger(name: str) -> logging.Logger:
    if name in _LOGGER_CACHE:
        logger = _LOGGER_CACHE[name]
        # Reconfigure if env changed (e.g., different log dir or level)
        desired_dir = _ensure_log_dir()
        desired_file = desired_dir / "qwen-cli.log"
        desired_level = _resolve_level()

        needs_reconfigure = False
        for h in list(logger.handlers):
            if isinstance(h, RotatingFileHandler):
                current_file = Path(getattr(h, 'baseFilename', ''))
                if current_file != desired_file:
                    needs_reconfigure = True
            # Also adjust levels dynamically
            h.setLevel(desired_level)
        if logger.level != desired_level:
            logger.setLevel(desired_level)

        if needs_reconfigure:
            for h in list(logger.handlers):
                try:
                    h.close()
                except Exception:
                    pass
                logger.removeHandler(h)
            # Fall through to fresh configuration below
        else:
            return logger

    logger = logging.getLogger(name)
    if logger.handlers:
        # Already configured globally
        _LOGGER_CACHE[name] = logger
        return logger

    logger.setLevel(_resolve_level())

    log_dir = _ensure_log_dir()
    logfile = log_dir / "qwen-cli.log"

    # Rotating file handler: 5 MB per file, keep 5 backups
    file_handler = RotatingFileHandler(
        filename=str(logfile), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    # Optional console handler
    if os.environ.get("QWEN_LOG_TO_CONSOLE", "1") == "1":
        console_handler = logging.StreamHandler()
        console_fmt = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_fmt)
        console_handler.setLevel(_resolve_level())
        logger.addHandler(console_handler)

    logger.propagate = False
    _LOGGER_CACHE[name] = logger
    return logger


