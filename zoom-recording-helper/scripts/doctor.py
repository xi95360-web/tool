from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import shutil
import socket
import sys
from dataclasses import dataclass
from pathlib import Path

from .audio_device import list_audio_devices
from .config import CONFIG_FILE, DEFAULT_CONFIG, load_config
from .obs_client import OBSClient, OBSClientError, tcp_reachable


@dataclass
class Check:
    level: str
    name: str
    detail: str
    critical: bool = False


def _app_exists(name: str) -> bool:
    return any((root / name).exists() for root in (Path("/Applications"), Path.home() / "Applications"))


def collect_checks(config: dict | None = None) -> list[Check]:
    config = config or load_config(require_file=False)
    checks: list[Check] = []
    is_macos = sys.platform == "darwin"
    checks.append(Check("PASS" if is_macos else "FAIL", "macOS", platform.platform(), True))
    arm = platform.machine() == "arm64"
    checks.append(Check("PASS" if arm else "FAIL", "Apple Silicon", platform.machine(), True))
    brew = shutil.which("brew")
    checks.append(Check("PASS" if brew else "FAIL", "Homebrew", brew or "安装: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""))
    obs = _app_exists("OBS.app")
    checks.append(Check("PASS" if obs else "FAIL", "OBS Studio", "已安装" if obs else "安装: brew install --cask obs", True))
    ffmpeg = shutil.which("ffmpeg")
    checks.append(Check("PASS" if ffmpeg else "FAIL", "ffmpeg", ffmpeg or "安装: brew install ffmpeg"))
    python = shutil.which("python3")
    checks.append(Check("PASS" if python else "FAIL", "Python 3", python or "安装: brew install python", True))
    obsws_package = importlib.util.find_spec("obsws_python") is not None
    checks.append(Check("PASS" if obsws_package else "FAIL", "OBS Python 客户端", "obsws-python 已安装" if obsws_package else "安装: ./zoom-record setup --install-python-deps", True))
    yaml_package = importlib.util.find_spec("yaml") is not None
    checks.append(Check("PASS" if yaml_package else "WARNING", "YAML 支持", "PyYAML 已安装" if yaml_package else "建议安装: ./zoom-record setup --install-python-deps"))
    switcher = shutil.which("SwitchAudioSource")
    checks.append(Check("PASS" if switcher else "WARNING", "SwitchAudioSource", switcher or "安装: brew install switchaudio-osx"))

    devices = list_audio_devices() if is_macos else []
    blackhole_name = str(config["system_audio_device"])
    blackhole = any(blackhole_name.casefold() in d.casefold() for d in devices) or Path("/Library/Audio/Plug-Ins/HAL/BlackHole2ch.driver").exists()
    checks.append(Check("PASS" if blackhole else "FAIL", "BlackHole 2ch", "已找到" if blackhole else "安装: brew install --cask blackhole-2ch", True))
    multi_name = str(config["multi_output_device"])
    multi = any(multi_name.casefold() in d.casefold() for d in devices)
    checks.append(Check("PASS" if multi else "FAIL", multi_name, "已找到" if multi else "请在“音频 MIDI 设置”中创建多输出设备", True))

    host, port = str(config["obs_websocket_host"]), int(config["obs_websocket_port"])
    websocket = tcp_reachable(host, port)
    if websocket and obsws_package:
        try:
            OBSClient(config)
            websocket_level, websocket_detail = "PASS", f"{host}:{port} 已连接并通过认证"
        except OBSClientError as exc:
            websocket_level, websocket_detail = "FAIL", str(exc)
    elif websocket:
        websocket_level, websocket_detail = "WARNING", f"{host}:{port} 端口可达；安装 Python 依赖后可验证认证"
    else:
        websocket_level, websocket_detail = "WARNING", "OBS 未运行、WebSocket 未启用或端口不可达"
    checks.append(Check(websocket_level, "OBS WebSocket", websocket_detail, websocket_level == "FAIL"))
    checks.append(Check("WARNING", "屏幕录制权限", "脚本无法可靠读取 TCC 状态；请在系统设置 → 隐私与安全性 → 屏幕与系统音频录制中确认 OBS 已开启"))
    checks.append(Check("WARNING", "麦克风权限", "脚本无法可靠读取 TCC 状态；请在系统设置 → 隐私与安全性 → 麦克风中确认 OBS 已开启"))
    checks.append(Check("PASS" if CONFIG_FILE.exists() else "WARNING", "配置文件", str(CONFIG_FILE) if CONFIG_FILE.exists() else "尚未创建；运行 ./zoom-record setup"))
    return checks


def print_checks(checks: list[Check]) -> None:
    print("Zoom Recording Helper 环境检查\n")
    for item in checks:
        print(f"[{item.level:<7}] {item.name}: {item.detail}")


def critical_failures(checks: list[Check]) -> list[Check]:
    return [item for item in checks if item.level == "FAIL" and item.critical]


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Zoom 录制环境")
    parser.add_argument("--open-privacy", action="store_true", help="打开 macOS 隐私设置")
    args = parser.parse_args()
    checks = collect_checks()
    print_checks(checks)
    if args.open_privacy and sys.platform == "darwin":
        os.system("open 'x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture'")
    failures = [c for c in checks if c.level == "FAIL"]
    print(f"\n结果: {len([c for c in checks if c.level == 'PASS'])} PASS, {len([c for c in checks if c.level == 'WARNING'])} WARNING, {len(failures)} FAIL")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
