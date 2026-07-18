from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # doctor/setup should remain usable before dependency install
    yaml = None

APP_NAME = "zoom-recording-helper"
CONFIG_DIR = Path(os.environ.get("ZOOM_RECORD_CONFIG_DIR", "~/.config/zoom-recording-helper")).expanduser()
CONFIG_FILE = CONFIG_DIR / "config.yaml"
SESSION_FILE = CONFIG_DIR / "current_session.json"
LOG_DIR = CONFIG_DIR / "logs"

DEFAULT_CONFIG: dict[str, Any] = {
    "recording_directory": os.environ.get("ZOOM_RECORD_RECORDING_DIR", "~/Movies/ZoomRecordings"),
    "obs_scene_name": "Zoom Recording",
    "obs_websocket_host": "localhost",
    "obs_websocket_port": 4455,
    "obs_websocket_password": "",
    "multi_output_device": "Zoom Multi-Output",
    "system_audio_device": "BlackHole 2ch",
    "microphone_device": "MacBook Microphone",
    "auto_open_zoom": True,
    "auto_open_obs": True,
    "extract_audio": True,
    "transcribe": False,
    "transcription_backend": "mlx-whisper",
    "transcription_model": "mlx-community/whisper-small-mlx",
    "whisper_cpp_binary": "whisper-cli",
    "whisper_cpp_model": "",
    "keep_original_mkv": True,
    "audio_tracks_separate": False,
}


class ConfigError(RuntimeError):
    pass


def ensure_directories() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _simple_yaml_dump(values: dict[str, Any]) -> str:
    lines = []
    for key, value in values.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif isinstance(value, str):
            rendered = f'"{value}"' if value == "" or ":" in value else value
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def write_default_config(overwrite: bool = False) -> Path:
    ensure_directories()
    if CONFIG_FILE.exists() and not overwrite:
        return CONFIG_FILE
    content = yaml.safe_dump(DEFAULT_CONFIG, allow_unicode=True, sort_keys=False) if yaml else _simple_yaml_dump(DEFAULT_CONFIG)
    CONFIG_FILE.write_text(content, encoding="utf-8")
    return CONFIG_FILE


def _simple_yaml_load(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ConfigError(f"无法解析配置行: {raw}")
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if value.lower() in {"true", "false"}:
            parsed: Any = value.lower() == "true"
        elif value.isdigit():
            parsed = int(value)
        else:
            parsed = value
        result[key.strip()] = parsed
    return result


def load_config(require_file: bool = True) -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        if require_file:
            raise ConfigError(f"配置文件不存在：{CONFIG_FILE}。请先运行 ./zoom-record setup")
        return dict(DEFAULT_CONFIG)
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
        loaded = yaml.safe_load(text) if yaml else _simple_yaml_load(text)
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            raise ConfigError("config.yaml 顶层必须是键值映射。")
    except ConfigError:
        raise
    except Exception as exc:
        raise ConfigError(f"无法读取配置文件：{exc}") from None
    config = {**DEFAULT_CONFIG, **loaded}
    config["recording_directory"] = str(Path(str(config["recording_directory"])).expanduser())
    try:
        config["obs_websocket_port"] = int(config["obs_websocket_port"])
    except (TypeError, ValueError):
        raise ConfigError("obs_websocket_port 必须是整数。") from None
    return config
