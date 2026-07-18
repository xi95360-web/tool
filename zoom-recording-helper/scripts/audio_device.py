from __future__ import annotations

import shutil

from .common import run_command


def list_audio_devices() -> list[str]:
    switcher = shutil.which("SwitchAudioSource")
    if switcher:
        result = run_command([switcher, "-a"])
        if result.returncode == 0:
            return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
    result = run_command(["system_profiler", "SPAudioDataType"], timeout=30)
    devices: list[str] = []
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if stripped.endswith(":") and not stripped.startswith(("Audio", "Devices")):
                devices.append(stripped[:-1])
    return sorted(set(devices))


def device_exists(name: str) -> bool:
    lowered = name.casefold()
    return any(lowered == device.casefold() or lowered in device.casefold() for device in list_audio_devices())


def current_output_device() -> str | None:
    switcher = shutil.which("SwitchAudioSource")
    if not switcher:
        return None
    result = run_command([switcher, "-c", "-t", "output"])
    return result.stdout.strip() if result.returncode == 0 else None


def set_output_device(name: str) -> tuple[bool, str]:
    switcher = shutil.which("SwitchAudioSource")
    if not switcher:
        return False, "未安装 SwitchAudioSource。请运行: brew install switchaudio-osx"
    result = run_command([switcher, "-s", name, "-t", "output"])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return False, f"无法切换到 {name}: {detail or '设备不存在'}"
    return True, result.stdout.strip() or name
