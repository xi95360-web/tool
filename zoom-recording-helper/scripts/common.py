from __future__ import annotations

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .config import LOG_DIR, ensure_directories


def get_logger(command: str) -> logging.Logger:
    ensure_directories()
    logger = logging.getLogger(f"zoom_record.{command}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_DIR / f"{datetime.now():%Y-%m-%d}.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    return logger


def run_command(args: Sequence[str], *, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)


def open_url(url: str) -> bool:
    try:
        return run_command(["open", url]).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def fail(message: str, code: int = 1) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return code


def expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()
