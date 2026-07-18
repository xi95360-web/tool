from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .config import SESSION_FILE, ensure_directories


class SessionError(RuntimeError):
    pass


def load_session(path: Path = SESSION_FILE) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SessionError(f"无法读取会话状态：{exc}") from None
    if not isinstance(data, dict):
        raise SessionError("会话状态格式无效。")
    return data


def save_session(data: dict[str, Any], path: Path = SESSION_FILE) -> None:
    if path == SESSION_FILE:
        ensure_directories()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def clear_session(path: Path = SESSION_FILE) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
